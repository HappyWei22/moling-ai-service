"""把自然语言解析成 UserRequirement：调用模型 → 抽取 JSON → 本地校验与状态裁定。

分工：
- 模型负责“读懂原话并抽取字段”；
- 本地 `finalize_requirement` 负责“按第 2 周协议收敛结果”，保证输出永远是合法的
  UserRequirement，非法值一律置 null 并记入 errors，信息不足一律标为需要追问，
  所以任何解析结果都不会因为格式问题把错误带进规划。
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from schemas import UserRequirement

from .config import Settings, get_settings
from .errors import ParseConfigError, ParseFormatError
from .llm_client import ChatClient, DashScopeChatClient, LLMResponse

PROMPT_FILES = {"v0": Path(__file__).parent / "prompt_v0.md"}
DEFAULT_PROMPT_VERSION = "v0"

SUPPORTED_STYLES = ("楷书", "行书", "行楷")
STYLE_ALIASES = {"楷体": "楷书", "行楷体": "行楷"}
OCCUPATION_ALIASES = {"老师": "教师", "小学生": "学生"}

PROTOCOL_FIELDS = (
    "occupation",
    "scene",
    "style",
    "duration_minutes",
    "goal",
    "exclusions",
    "status",
    "follow_up",
    "errors",
)

FOLLOW_UPS = {
    "style": "你想练哪种书体？目前可以按楷书、行书或行楷来规划。",
    "duration_minutes": "你每次大约想练几分钟？目前可以按5、15或30分钟来规划。",
    "personalization": "你主要想把练字用在哪种场景，或者希望改善什么？比如日常书写、学习、工作，或者字迹工整度。",
}
FALLBACK_FOLLOW_UP = "当前输入有冲突或非法值，请确认或重新提供后我再继续。"
VALID_STATUSES = ("complete", "needs_clarification", "conflict", "invalid")


@dataclass
class ParseOutcome:
    """一次解析的完整结果，字段足够写进 parse_runs.jsonl。"""

    requirement: UserRequirement
    raw_text: str
    client: str
    model: str
    prompt_version: str
    prompt_sha256: str
    temperature: float | None
    latency_ms: int
    usage: dict[str, Any] | None = None
    warnings: list[str] = field(default_factory=list)
    missing_keys: list[str] = field(default_factory=list)
    attempts: int = 1
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def usage_missing(self) -> bool:
        return self.usage is None


def prompt_path(version: str) -> Path:
    if version not in PROMPT_FILES:
        raise ParseConfigError(
            f"未知的提示词版本：{version}",
            hint=f"可用版本：{', '.join(sorted(PROMPT_FILES))}",
        )
    return PROMPT_FILES[version]


def load_prompt(version: str = DEFAULT_PROMPT_VERSION) -> tuple[str, str]:
    """返回 (提示词全文, sha256 前 12 位)，用于把提示词版本写进运行记录。"""
    path = prompt_path(version)
    if not path.exists():
        raise ParseConfigError(f"提示词文件不存在：{path}")
    text = path.read_text(encoding="utf-8")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return text, digest


def extract_json_object(text: str) -> dict[str, Any]:
    """从模型文本里取出 JSON 对象，容忍代码围栏和前后解释文字。"""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    candidates = [cleaned]
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start != -1 and end > start:
        candidates.append(cleaned[start:end + 1])

    for candidate in candidates:
        if not candidate:
            continue
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed

    raise ParseFormatError(
        "模型输出不是可解析的 JSON 对象", raw_text=text
    )


def _clean_text(value: Any, field_name: str, warnings: list[str]) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        warnings.append(f"{field_name} 不是字符串，已按 null 处理")
        return None
    stripped = value.strip()
    return stripped or None


def _clean_duration(value: Any, warnings: list[str]) -> int | None:
    """只接受正整数；非法值返回 None，由调用方记入 errors。"""
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, str) and value.strip().isdigit():
        warnings.append("duration_minutes 返回了字符串，已转换为整数")
        value = int(value.strip())
    if not isinstance(value, int) or value < 1:
        return None
    return value


def _clean_errors(value: Any, warnings: list[str]) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        warnings.append("errors 不是数组，已按 [] 处理")
        return []
    cleaned: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            warnings.append("errors 中存在非对象项，已丢弃")
            continue
        error_type = item.get("type")
        error_field = item.get("field")
        if not isinstance(error_type, str) or not error_type.strip():
            warnings.append("errors 中存在缺少 type 的项，已丢弃")
            continue
        if not isinstance(error_field, str):
            error_field = ""
        record = {"type": error_type.strip(), "field": error_field.strip()}
        if "value" in item:
            record["value"] = item["value"]
        key = json.dumps(record, ensure_ascii=False, sort_keys=True, default=str)
        if key in seen:
            warnings.append("errors 中存在重复项，已去重")
            continue
        seen.add(key)
        cleaned.append(record)
    return cleaned


def _add_error(errors: list[dict[str, Any]], error_type: str, field_name: str, value: Any) -> None:
    for existing in errors:
        if existing["type"] == error_type and existing["field"] == field_name and existing.get("value") == value:
            return
    errors.append({"type": error_type, "field": field_name, "value": value})


def finalize_requirement(candidate: dict[str, Any]) -> tuple[UserRequirement, list[str]]:
    """把模型的候选对象收敛成合法协议；永不抛出模型内容相关的异常。"""
    warnings: list[str] = []

    occupation = _clean_text(candidate.get("occupation"), "occupation", warnings)
    if occupation:
        occupation = OCCUPATION_ALIASES.get(occupation, occupation)
    scene = _clean_text(candidate.get("scene"), "scene", warnings)
    goal = _clean_text(candidate.get("goal"), "goal", warnings)

    style_raw = candidate.get("style")
    style = _clean_text(style_raw, "style", warnings)
    if style is not None:
        style = STYLE_ALIASES.get(style, style)
    errors = _clean_errors(candidate.get("errors"), warnings)

    if style is not None and style not in SUPPORTED_STYLES:
        _add_error(errors, "unsupported_style_value", "style", style_raw)
        style = None
        warnings.append(f"书体 {style_raw!r} 不在支持范围内，已置 null 并记入 errors")

    duration_raw = candidate.get("duration_minutes")
    duration = _clean_duration(duration_raw, warnings)
    if duration_raw is not None and duration is None:
        _add_error(errors, "invalid_value", "duration_minutes", duration_raw)
        warnings.append("时长不是合法正整数，已置 null 并记入 errors")

    exclusions_raw = candidate.get("exclusions")
    exclusions: list[str] = []
    if exclusions_raw is None:
        pass
    elif not isinstance(exclusions_raw, list):
        warnings.append("exclusions 不是数组，已按 [] 处理")
    else:
        for item in exclusions_raw:
            if isinstance(item, str) and item.strip():
                exclusions.append(item.strip())
            else:
                warnings.append("exclusions 中存在空值或非字符串项，已丢弃")

    status = candidate.get("status")
    if status not in VALID_STATUSES:
        warnings.append(f"status {status!r} 不在协议内，已按缺失处理")
        status = None
    follow_up = _clean_text(candidate.get("follow_up"), "follow_up", warnings)

    # 状态裁定：errors 优先，其次补追问，最后才允许 complete。
    if errors:
        status = "conflict" if status == "conflict" else "invalid"
    else:
        missing: list[str] = []
        if style is None:
            missing.append("style")
        elif duration is None:
            missing.append("duration_minutes")
        elif occupation is None and scene is None and goal is None:
            missing.append("personalization")

        if missing:
            status = "needs_clarification"
            if not follow_up:
                follow_up = FOLLOW_UPS[missing[0]]
            warnings.append(f"信息不足（{missing[0]}），已标为 needs_clarification")
        elif status in (None, "needs_clarification"):
            status = "complete"
            warnings.append("字段已满足生成条件，状态已修正为 complete")
        elif status == "conflict":
            _add_error(errors, "unresolved_conflict", "status", "conflict")
            status = "invalid"
            warnings.append("模型标记冲突但没有错误明细，已改判为 invalid")
        elif status == "invalid":
            _add_error(errors, "invalid_but_no_detail", "status", None)
            warnings.append("模型标记非法但没有错误明细，已补记错误")

    if status == "complete":
        follow_up = None
    elif not follow_up:
        follow_up = FALLBACK_FOLLOW_UP

    payload = {
        "occupation": occupation,
        "scene": scene,
        "style": style,
        "duration_minutes": duration,
        "goal": goal,
        "exclusions": exclusions,
        "status": status,
        "follow_up": follow_up,
        "errors": errors,
    }
    try:
        requirement = UserRequirement.model_validate(payload)
    except ValidationError as error:  # pragma: no cover - 兜底，正常路径不会触发
        raise ParseFormatError(f"本地校验未能把模型输出修复为合法需求：{error}") from error
    return requirement, warnings


def build_client(settings: Settings) -> ChatClient:
    return DashScopeChatClient(settings)


def parse_text(
    text: str,
    *,
    client: ChatClient | None = None,
    settings: Settings | None = None,
) -> ParseOutcome:
    """解析一句自然语言需求。真实调用需要密钥，离线验收可传入 MockChatClient。"""
    if not isinstance(text, str) or not text.strip():
        raise ParseFormatError("待解析文本为空")

    settings_warnings: list[str] = []
    if settings is None:
        settings, settings_warnings = get_settings()
    version = settings.prompt_version
    prompt_text, prompt_digest = load_prompt(version)

    if client is None:
        client = build_client(settings)

    started = time.perf_counter()
    response: LLMResponse = client.complete(prompt_text, text.strip())
    latency_ms = int((time.perf_counter() - started) * 1000)

    candidate = extract_json_object(response.text)
    missing_keys = [name for name in PROTOCOL_FIELDS if name not in candidate]
    if len(missing_keys) == len(PROTOCOL_FIELDS):
        raise ParseFormatError("模型输出没有任何协议字段", raw_text=response.text, missing_keys=missing_keys)

    requirement, warnings = finalize_requirement(candidate)
    warnings = settings_warnings + warnings
    if missing_keys:
        warnings.append("模型输出缺少字段：" + "、".join(missing_keys))

    return ParseOutcome(
        requirement=requirement,
        raw_text=response.text,
        client=getattr(client, "name", "unknown"),
        model=response.model,
        prompt_version=version,
        prompt_sha256=prompt_digest,
        temperature=settings.temperature if getattr(client, "name", None) != "mock" else None,
        latency_ms=latency_ms,
        usage=response.usage,
        warnings=warnings,
        missing_keys=missing_keys,
        extra=response.extra,
    )
