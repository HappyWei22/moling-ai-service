"""评估本机（或任一 Ollama 主机）能跑哪些模型，以及跑得动多快。

用途：在没有正式跑批之前，先回答「这套硬件能上哪个尺寸的模型」。
      对每个模型给出：能否全量上卡、显存占用、生成速度、JSON 合规率。

用法：
    # 列出本机已有模型并全部测一遍
    python bench_local_models.py --all

    # 只测指定的
    python bench_local_models.py --models qwen2.5:7b-instruct-q4_k_m qwen2.5:14b-instruct-q4_k_m

    # 用 v2 评测集的真实输入测（默认就是）
    python bench_local_models.py --all --samples v2_eval/samples_v2.jsonl --limit 8

    # 只打印报告不写文件
    python bench_local_models.py --all --dry-run

输出：
    - 控制台 markdown 表格
    - <out> 指定的 json（默认 v2_eval/baseline/model_bench.json）

注意：**速度只能实测，不能估算**。本脚本存在的意义就是把「大概能跑」变成实测数字。
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _device  # noqa: E402  本地硬件快照，见 _device.py

OLLAMA = os.environ.get("MOLING_OLLAMA_BASE", "http://127.0.0.1:11434").rstrip("/")
if OLLAMA.endswith("/v1"):
    OLLAMA = OLLAMA[:-3]  # 允许直接复用跑批脚本的同一个环境变量
# 不走系统代理：Windows 注册表里的代理会连累 127.0.0.1
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _get(path: str, timeout: float = 30.0) -> dict:
    with OPENER.open(f"{OLLAMA}{path}", timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _post(path: str, payload: dict, timeout: float = 600.0) -> dict:
    req = urllib.request.Request(
        f"{OLLAMA}{path}",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with OPENER.open(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def list_models() -> list[str]:
    return [m["name"] for m in _get("/api/tags").get("models", [])]


def model_detail(name: str) -> dict:
    """拿参数量、量化、上下文长度。"""
    try:
        info = _post("/api/show", {"model": name})
    except urllib.error.HTTPError:
        return {}
    details = info.get("details") or {}
    return {
        "parameter_size": details.get("parameter_size"),
        "quantization_level": details.get("quantization_level"),
        "family": details.get("family"),
        "context_length": (info.get("model_info") or {}).get(
            f"{details.get('family')}.context_length"
        ),
    }


def running_snapshot(name: str) -> dict:
    """从 /api/ps 读当前加载情况：size 是总占用，size_vram 是上卡部分。

    size_vram / size 就是「有多少跑在 GPU 上」——这是判断会不会被 CPU 拖慢的关键。
    """
    for item in _get("/api/ps").get("models", []):
        if item.get("name") == name or item.get("model") == name:
            size = item.get("size") or 0
            vram = item.get("size_vram") or 0
            return {
                "size_gb": round(size / 1024 ** 3, 2),
                "size_vram_gb": round(vram / 1024 ** 3, 2),
                "gpu_ratio": round(vram / size, 3) if size else None,
            }
    return {}


def gpu_mem_used_mb() -> int | None:
    if not shutil.which("nvidia-smi"):
        return None
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip().splitlines()
        return max(int(x) for x in out) if out else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def load_samples(path: Path, limit: int) -> list[str]:
    texts = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("split") == "sealed":  # 封存集不碰
                continue
            texts.append(row["input"])
            if len(texts) >= limit:
                break
    return texts


REQUIRED_KEYS = {"occupation", "scene", "font", "duration_minutes", "status", "errors"}


def json_compliance(text: str) -> tuple[bool, str]:
    """模型输出是不是**严格合规**的 6 字段 JSON。

    比「能不能解析」更严：多字段、少字段、非 JSON 都算不合规 ——
    因为上游 `ParsedRequirementV2` 是 extra="forbid"。
    """
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = "\n".join(cleaned.splitlines()[1:]).rsplit("```", 1)[0]
    try:
        obj = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        return False, f"非 JSON（{exc.msg}）"
    if not isinstance(obj, dict):
        return False, "顶层不是对象"
    keys = set(obj)
    if keys != REQUIRED_KEYS:
        extra = keys - REQUIRED_KEYS
        miss = REQUIRED_KEYS - keys
        bits = []
        if extra:
            bits.append(f"多 {sorted(extra)}")
        if miss:
            bits.append(f"少 {sorted(miss)}")
        return False, "；".join(bits)
    return True, ""


def bench_one(name: str, texts: list[str], prompt: str) -> dict:
    print(f"\n=== {name} ===")
    result: dict = {"model": name, **model_detail(name)}

    # 预热：把模型加载进显存，否则首条会把加载时间算进去
    t0 = time.perf_counter()
    try:
        _post("/api/chat", {
            "model": name,
            "messages": [{"role": "system", "content": prompt},
                         {"role": "user", "content": "我是老师，练15分钟楷书。"}],
            "stream": False, "options": {"temperature": 0},
        })
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        print(f"  !! 加载失败 HTTP {exc.code}：{detail}")
        result["error"] = f"HTTP {exc.code}: {detail}"
        return result
    except (urllib.error.URLError, TimeoutError) as exc:
        result["error"] = f"连接失败：{exc}"
        print(f"  !! {result['error']}")
        return result
    result["load_seconds"] = round(time.perf_counter() - t0, 2)

    ps = running_snapshot(name)
    result.update(ps)
    mem0 = gpu_mem_used_mb()

    latencies, out_tokens, ok, reasons = [], 0, 0, []
    for idx, text in enumerate(texts, 1):
        started = time.perf_counter()
        try:
            data = _post("/api/chat", {
                "model": name,
                "messages": [{"role": "system", "content": prompt},
                             {"role": "user", "content": text}],
                "stream": False,
                "format": "json",
                "options": {"temperature": 0},
            })
        except (urllib.error.URLError, TimeoutError, urllib.error.HTTPError) as exc:
            print(f"  [{idx}/{len(texts)}] 失败：{exc}")
            continue
        elapsed = time.perf_counter() - started
        latencies.append(elapsed)

        content = (data.get("message") or {}).get("content") or ""
        eval_count = data.get("eval_count") or 0
        out_tokens += eval_count
        good, why = json_compliance(content)
        ok += good
        if not good:
            reasons.append(why)
        print(f"  [{idx}/{len(texts)}] {elapsed:5.2f}s  "
              f"{eval_count} tok  {'JSON合规' if good else '不合规：' + why}")

    mem1 = gpu_mem_used_mb()
    result.update({
        "samples": len(latencies),
        "json_compliance": f"{ok}/{len(latencies)}",
        "json_compliance_pct": round(ok / len(latencies) * 100, 1) if latencies else None,
        "compliance_failures": sorted(set(reasons)),
        "latency_mean_s": round(statistics.mean(latencies), 3) if latencies else None,
        "latency_p50_s": round(statistics.median(latencies), 3) if latencies else None,
        "latency_max_s": round(max(latencies), 3) if latencies else None,
        "throughput_tok_s": round(out_tokens / sum(latencies), 1) if latencies else None,
        "est_full_batch_min": round(statistics.mean(latencies) * 98 / 60, 1) if latencies else None,
        "gpu_mem_delta_mb": (mem1 - mem0) if (mem0 is not None and mem1 is not None) else None,
    })
    print(f"  → 均值 {result['latency_mean_s']}s / {result['throughput_tok_s']} tok/s "
          f"/ GPU占比 {(result.get('gpu_ratio') or 0) * 100:.0f}% "
          f"/ 98条预计 {result['est_full_batch_min']} 分钟")
    return result


def to_markdown(rows: list[dict], gpu_total_mb: int | None, host: dict | None = None) -> str:
    lines = []
    if host:
        lines.append(f"> 机器：`{host.get('host') or '?'}` / {host.get('platform') or '?'} / "
                     f"{_device.one_line(host)}")
        lines.append("")
    lines.append("| 模型 | 参数量 | 量化 | 加载 | 上卡占比 | 单条均值 | tok/s | JSON合规 | 98条预计 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        if r.get("error"):
            lines.append(f"| `{r['model']}` | {r.get('parameter_size') or '-'} | - | - | - | - | - | **失败** | - |")
            continue
        ratio = r.get("gpu_ratio")
        ratio_txt = f"{ratio * 100:.0f}%" if ratio is not None else "未采集"
        flag = "" if ratio is None or ratio >= 0.99 else " ⚠️部分CPU"
        lines.append(
            f"| `{r['model']}` | {r.get('parameter_size') or '-'} | {r.get('quantization_level') or '-'} "
            f"| {r.get('load_seconds')}s | {ratio_txt}{flag} | {r.get('latency_mean_s')}s "
            f"| {r.get('throughput_tok_s')} | {r.get('json_compliance')} "
            f"({r.get('json_compliance_pct')}%) | {r.get('est_full_batch_min')} min |"
        )
    if gpu_total_mb:
        lines.append("")
        lines.append(f"> 显卡总量 {gpu_total_mb} MB。`上卡占比` < 100% 说明有层被放到 CPU，"
                     f"会被处理器核数拖慢——4 核 Xeon 上这一项尤其要盯。")
    return "\n".join(lines)


def main() -> int:
    here = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="评估本机可跑模型与速度")
    parser.add_argument("--models", nargs="*", default=None)
    parser.add_argument("--all", action="store_true", help="测本机全部已装模型")
    parser.add_argument("--samples", default=str(here / "v2_eval/samples_v2.jsonl"))
    parser.add_argument("--limit", type=int, default=8, help="每个模型跑几条（默认 8）")
    parser.add_argument("--out", default=str(here / "v2_eval/baseline/model_bench.json"))
    parser.add_argument("--dry-run", action="store_true", help="只打印不写文件")
    args = parser.parse_args()

    if args.all:
        models = list_models()
    elif args.models:
        models = args.models
    else:
        parser.error("请给 --models ... 或 --all")
    if not models:
        print("没有可测的模型（ollama list 为空）")
        return 2

    samples = Path(args.samples)
    prompt_path = here / "parsing/prompt_v2.md"
    if not samples.exists() or not prompt_path.exists():
        print(f"找不到样本或提示词：{samples} / {prompt_path}")
        return 2
    texts = load_samples(samples, args.limit)
    prompt = prompt_path.read_text(encoding="utf-8")

    host = _device.snapshot()
    gpu_total = host.get("gpu_total_mb")

    print(f"待测 {len(models)} 个模型，每个 {len(texts)} 条真实样本"
          f"（提示词 {prompt_path.name}）")
    print(f"机器：{host['host']} / {_device.one_line(host)}")

    rows = [bench_one(m, texts, prompt) for m in models]

    table = to_markdown(rows, gpu_total, host)
    print("\n" + table)

    if not args.dry_run:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "host": host,
            "gpu_total_mb": gpu_total,
            "samples_per_model": len(texts),
            "samples_file": str(samples),
            "prompt_sha256_prefix": __import__("hashlib").sha256(
                prompt.encode("utf-8")).hexdigest()[:12],
            "results": rows,
        }
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        md = out.with_suffix(".md")
        md.write_text("# 本机可跑模型实测\n\n" + table + "\n", encoding="utf-8")
        print(f"\n已写入 {out}\n已写入 {md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
