"""无会话状态的 v2 解析。会话历史由后端保存并作为 text 传入。"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from schemas import ParsedRequirementV2

from .config import Settings, get_settings
from .errors import ParseFormatError
from .llm_client import ChatClient, DashScopeChatClient
from .parse_requirement import extract_json_object

PROMPT_PATH = Path(__file__).with_name("prompt_v2.md")
FONTS = {"楷书", "行书", "行楷"}
FONT_ALIASES = {"楷体": "楷书", "行楷体": "行楷"}
DURATIONS = {5, 15, 30}


@dataclass
class ParseV2Outcome:
    requirement: ParsedRequirementV2
    message: str
    client: str
    model: str
    prompt_sha256: str


def _clean_text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    return value.strip() or None


def _collect_errors(candidate: dict[str, Any], values: dict[str, Any]) -> list[dict[str, Any]]:
    """合并模型错误和本地校验结果；同一问题只提示一次。"""
    errors: list[dict[str, Any]] = []

    def add(error_type: str, field: str, value: Any = None) -> None:
        if not any(item["type"] == error_type and item["field"] == field for item in errors):
            errors.append({"type": error_type, "field": field, "value": value})

    model_errors = candidate.get("errors")
    if isinstance(model_errors, list):
        for item in model_errors:
            if not isinstance(item, dict):
                continue
            error_type = _clean_text(item.get("type"))
            field = _clean_text(item.get("field"))
            # 缺失由本地统一判断，避免模型误报或重复报告组合条件。
            if error_type and field and error_type != "missing_field":
                add(error_type, field, item.get("value"))

    for field, supported in (("font", FONTS), ("duration_minutes", DURATIONS)):
        raw = candidate.get(field)
        value = values[field]
        if raw is not None and (value is None or value not in supported):
            add("invalid_value", field, raw)

    for item in errors:
        if item["field"] in values:
            values[item["field"]] = None

    for field in ("font", "duration_minutes"):
        if values[field] is None and not any(item["field"] == field for item in errors):
            add("missing_field", field)
    if values["occupation"] is None and values["scene"] is None:
        if not any(item["field"] in ("occupation", "scene", "personalization") for item in errors):
            add("missing_field", "personalization")

    # 保留模型无明细的异常状态，不能据此放行，但也不能丢掉其他缺失项。
    if candidate.get("status") == "invalid" and not any(
        item["type"] not in ("missing_field", "conflicting_values") for item in errors
    ):
        add("invalid_value", "requirement")
    if candidate.get("status") == "conflict" and not any(
        item["type"] == "conflicting_values" for item in errors
    ):
        add("conflicting_values", "requirement")
    order = {"font": 0, "duration_minutes": 1, "occupation": 2, "scene": 3, "personalization": 4}
    return sorted(errors, key=lambda item: order.get(item["field"], 5))


def _error_message(error: dict[str, Any]) -> str:
    field = error["field"]
    label = {"font": "书体", "duration_minutes": "练习时长", "occupation": "职业",
             "scene": "书写场景", "personalization": "职业或书写场景"}.get(field, "需求信息")
    if error["type"] == "missing_field":
        return {
            "font": "你想练哪种书体？目前支持楷书、行书或行楷。",
            "duration_minutes": "你每次想练几分钟？目前支持5、15或30分钟。",
            "personalization": "你是什么职业，或者主要在哪种场景使用书写？",
        }.get(field, f"请补充{label}。")
    if error["type"] == "conflicting_values":
        return f"{label}存在冲突，请确认本次以哪个为准。"
    value = error.get("value")
    detail = f"（你提供的是{value}）" if value is not None else ""
    if field == "font":
        return f"书体不在支持范围内{detail}，请选择楷书、行书或行楷。"
    if field == "duration_minutes":
        return f"练习时长不符合要求{detail}，请选择5、15或30分钟。"
    return f"{label}存在非法或不支持的内容{detail}，请修改或重新提供。"


def finalize_v2(candidate: dict[str, Any]) -> tuple[ParsedRequirementV2, str]:
    """本地汇总全部问题、裁定状态并生成追问，不采用模型追问。"""
    occupation = _clean_text(candidate.get("occupation"))
    occupation = {"老师": "教师", "小学生": "学生"}.get(occupation, occupation)
    raw_font = _clean_text(candidate.get("font"))
    duration = candidate.get("duration_minutes")
    if isinstance(duration, str) and duration.strip().isdigit():
        duration = int(duration.strip())
    if isinstance(duration, bool) or not isinstance(duration, int):
        duration = None
    values = {
        "occupation": occupation,
        "scene": _clean_text(candidate.get("scene")),
        "font": FONT_ALIASES.get(raw_font, raw_font),
        "duration_minutes": duration,
    }
    errors = _collect_errors(candidate, values)
    error_types = {item["type"] for item in errors}
    if error_types - {"missing_field", "conflicting_values"}:
        status = "invalid"
    elif "conflicting_values" in error_types:
        status = "conflict"
    elif errors:
        status = "needs_clarification"
    else:
        status = "complete"

    messages = [_error_message(item) for item in errors]
    if not messages:
        message = "ok"
    elif len(messages) == 1:
        message = messages[0]
    else:
        message = "请补充或修改以下信息：" + " ".join(
            f"{index}. {text}" for index, text in enumerate(messages, 1)
        )
    return ParsedRequirementV2(**values, status=status), message


def parse_text_v2(
    text: str, *, client: ChatClient | None = None, settings: Settings | None = None,
) -> ParseV2Outcome:
    if not isinstance(text, str) or not text.strip():
        raise ParseFormatError("待解析文本为空")
    if settings is None:
        settings, _ = get_settings()
    prompt = PROMPT_PATH.read_text(encoding="utf-8")
    if client is None:
        client = DashScopeChatClient(settings)
    response = client.complete(prompt, text.strip())
    candidate = extract_json_object(response.text)
    if not any(key in candidate for key in ("occupation", "scene", "font", "duration_minutes")):
        raise ParseFormatError("模型输出没有任何 v2 需求字段", raw_text=response.text)
    requirement, message = finalize_v2(candidate)
    return ParseV2Outcome(
        requirement=requirement,
        message=message,
        client=client.name,
        model=response.model,
        prompt_sha256=hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12],
    )
