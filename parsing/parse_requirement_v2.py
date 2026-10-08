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


def _first_error(errors: Any, field: str) -> bool:
    return isinstance(errors, list) and any(
        isinstance(item, dict) and item.get("field") == field for item in errors
    )


def finalize_v2(candidate: dict[str, Any]) -> tuple[ParsedRequirementV2, str]:
    """本地决定状态，不允许模型仅靠自报 complete 越过缺失或非法值。"""
    occupation = _clean_text(candidate.get("occupation"))
    if occupation in ("老师", "小学生"):
        occupation = {"老师": "教师", "小学生": "学生"}[occupation]
    scene = _clean_text(candidate.get("scene"))

    raw_font = _clean_text(candidate.get("font"))
    font = FONT_ALIASES.get(raw_font, raw_font)
    raw_duration = candidate.get("duration_minutes")
    duration = raw_duration
    if isinstance(duration, str) and duration.strip().isdigit():
        duration = int(duration.strip())
    if isinstance(duration, bool) or not isinstance(duration, int):
        duration = None

    errors = candidate.get("errors")
    font_error = _first_error(errors, "font") or (raw_font is not None and font not in FONTS)
    duration_error = _first_error(errors, "duration_minutes") or (
        raw_duration is not None and duration not in DURATIONS
    )
    if font_error:
        font = None
    if duration_error:
        duration = None

    conflict = candidate.get("status") == "conflict" or (
        isinstance(errors, list) and any(
            isinstance(item, dict) and item.get("type") == "conflicting_values"
            for item in errors
        )
    )
    invalid = (raw_font is not None and FONT_ALIASES.get(raw_font, raw_font) not in FONTS) or (
        raw_duration is not None and duration not in DURATIONS
    ) or (isinstance(errors, list) and any(
        isinstance(item, dict) and item.get("type") != "conflicting_values"
        for item in errors
    ))
    if invalid:
        status = "invalid"
    elif conflict:
        status = "conflict"
    elif candidate.get("status") == "invalid":
        status = "invalid"
    elif font is None or duration is None or (occupation is None and scene is None):
        status = "needs_clarification"
    else:
        status = "complete"

    if status == "complete":
        message = "ok"
    else:
        follow_up = _clean_text(candidate.get("follow_up"))
        if font_error or font is None:
            fallback = "你想练哪种书体？目前支持楷书、行书或行楷。"
        elif duration_error or duration is None:
            fallback = "你每次想练几分钟？目前支持5、15或30分钟。"
        elif occupation is None and scene is None:
            fallback = "你是什么职业，或者主要在哪种场景练字？"
        else:
            fallback = "信息有冲突，请确认本次的书体和练习时长。"
        message = follow_up or fallback

    return ParsedRequirementV2(
        occupation=occupation,
        scene=scene,
        font=font,
        duration_minutes=duration,
        status=status,
    ), message


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
