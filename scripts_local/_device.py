"""采集本机硬件信息，供跑批脚本写「这份结果跑在哪台机器上」。

为什么单独抽一个模块：`run_local_ollama.py` 与 `bench_local_models.py` 都要用，
而且上游的运行记录里**没有硬件字段** —— 同一个模型跑在不同机器上，事后无法区分。
2026-10-23 就因为这点，需要人工翻 `nvidia-smi` 才能回答「这些数字是哪台机器跑的」。
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess


#: `nvidia-smi` 在 Windows 上不一定进 PATH —— 新版驱动装在 System32，
#: 老版装在 Program Files 下。只靠 `shutil.which` 会在「驱动明明装了」时报未检测到。
_NVIDIA_SMI_FALLBACKS = (
    r"C:\Windows\System32\nvidia-smi.exe",
    r"C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe",
)


def _nvidia_smi() -> str | None:
    found = shutil.which("nvidia-smi")
    if found:
        return found
    for candidate in _NVIDIA_SMI_FALLBACKS:
        if os.path.isfile(candidate):
            return candidate
    return None


def _gpu_list() -> list[str] | None:
    smi = _nvidia_smi()
    if not smi:
        return None
    try:
        out = subprocess.run(
            [smi, "--query-gpu=name,memory.total,driver_version",
             "--format=csv,noheader"],
            capture_output=True, text=True, timeout=15,
        ).stdout
        return [line.strip() for line in out.splitlines() if line.strip()] or None
    except (OSError, subprocess.SubprocessError):
        return None


def _ram_gb() -> float | None:
    try:
        if platform.system() == "Windows":
            import ctypes

            class _MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            stat = _MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(_MEMORYSTATUSEX)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
                return round(stat.ullTotalPhys / 1024 ** 3, 1)
        else:
            with open("/proc/meminfo", encoding="utf-8") as handle:
                for line in handle:
                    if line.startswith("MemTotal:"):
                        return round(int(line.split()[1]) / 1024 ** 2, 1)
    except Exception:  # noqa: BLE001 - 采集失败绝不能影响跑批
        pass
    return None


def _gpu_total_mb() -> int | None:
    smi = _nvidia_smi()
    if not smi:
        return None
    try:
        out = subprocess.run(
            [smi, "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10,
        ).stdout
        values = [int(x) for x in out.strip().splitlines() if x.strip()]
        return max(values) if values else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def snapshot() -> dict:
    gpus = _gpu_list()
    return {
        "host": platform.node(),
        "platform": platform.platform(),
        "cpu_logical_cores": os.cpu_count(),
        "ram_gb": _ram_gb(),
        "gpus": gpus,
        "gpu_total_mb": _gpu_total_mb(),
    }


def one_line(info: dict) -> str:
    gpu = (info.get("gpus") or ["未检测到 nvidia-smi"])[0]
    return (f"CPU {info.get('cpu_logical_cores')} 线程 / RAM {info.get('ram_gb')} GB / GPU {gpu}")
