"""解析模块的配置：环境变量、.env 读取与运行参数。

密钥只从环境变量或项目根目录的 .env 读取，不写入代码、日志或运行记录。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_MODEL = "qwen-plus"
DEFAULT_TIMEOUT_SECONDS = 60.0
DEFAULT_TEMPERATURE = 0.0


def load_dotenv(path: Path | None = None) -> None:
    """把 .env 中的键值读入环境变量；已存在的变量不覆盖。"""
    env_path = path or PROJECT_ROOT / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _read_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    """一次解析调用需要的全部配置。"""

    base_url: str
    model: str
    api_key: str | None
    timeout_seconds: float
    temperature: float
    extra_body: dict
    prompt_version: str

    @property
    def allow_network(self) -> bool:
        return bool(self.api_key)

    @property
    def endpoint(self) -> str:
        return self.base_url.rstrip("/") + "/chat/completions"

    @property
    def base_url_host(self) -> str:
        """只保留主机名，便于写进运行记录而不泄露完整路径。"""
        without_scheme = self.base_url.split("//", 1)[-1]
        return without_scheme.split("/", 1)[0]


def _parse_extra_body(raw: str) -> tuple[dict, str | None]:
    import json

    text = raw.strip()
    if not text:
        return {}, None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as error:
        return {}, f"MOLING_LLM_EXTRA_BODY 不是合法 JSON（{error.msg}），已忽略"
    if not isinstance(parsed, dict):
        return {}, "MOLING_LLM_EXTRA_BODY 必须是 JSON 对象，已忽略"
    return parsed, None


def get_settings() -> tuple[Settings, list[str]]:
    """读取配置，返回 (配置, 警告列表)。缺少密钥不算错误，由调用方决定如何处理。"""
    load_dotenv()
    warnings: list[str] = []
    extra_body, extra_warning = _parse_extra_body(os.environ.get("MOLING_LLM_EXTRA_BODY", ""))
    if extra_warning:
        warnings.append(extra_warning)
    api_key = (
        os.environ.get("MOLING_LLM_API_KEY", "").strip()
        or os.environ.get("DASHSCOPE_API_KEY", "").strip()
        or None
    )
    settings = Settings(
        base_url=os.environ.get("MOLING_LLM_BASE_URL", "").strip() or DEFAULT_BASE_URL,
        model=os.environ.get("MOLING_LLM_MODEL", "").strip() or DEFAULT_MODEL,
        api_key=api_key,
        timeout_seconds=_read_float("MOLING_LLM_TIMEOUT", DEFAULT_TIMEOUT_SECONDS),
        temperature=_read_float("MOLING_LLM_TEMPERATURE", DEFAULT_TEMPERATURE),
        extra_body=extra_body,
        prompt_version=os.environ.get("MOLING_LLM_PROMPT_VERSION", "").strip() or "v1",
    )
    return settings, warnings
