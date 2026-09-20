"""模型调用层：OpenAI 兼容的 chat/completions 客户端，以及离线用的固定响应客户端。

只依赖标准库，避免为一次结构化抽取增加新依赖。真实调用需要密钥；
没有密钥时可用 MockChatClient 走通同一套解析与校验流程（运行记录会标记 client=mock）。
"""

from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from .config import Settings
from .errors import ParseConfigError, ParseTransportError

MAX_ERROR_BODY_CHARS = 400


@dataclass
class LLMResponse:
    """模型返回的文本与可记录的元信息。"""

    text: str
    model: str
    usage: dict[str, Any] | None = None
    extra: dict[str, Any] = field(default_factory=dict)


class ChatClient(Protocol):
    name: str

    def complete(self, system_prompt: str, user_text: str) -> LLMResponse: ...


def _truncate(text: str, limit: int = MAX_ERROR_BODY_CHARS) -> str:
    text = text.strip().replace("\n", " ")
    return text if len(text) <= limit else text[:limit] + "…"


class DashScopeChatClient:
    """OpenAI 兼容接口客户端，默认指向阿里云百炼（DashScope）。"""

    name = "dashscope"

    def __init__(self, settings: Settings):
        if not settings.api_key:
            raise ParseConfigError(
                "缺少模型密钥，无法进行真实调用",
                hint="在项目根目录 .env 中设置 DASHSCOPE_API_KEY（见 .env.example）",
            )
        self.settings = settings

    def build_payload(self, system_prompt: str, user_text: str) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.settings.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            "temperature": self.settings.temperature,
            "response_format": {"type": "json_object"},
        }
        payload.update(self.settings.extra_body)
        return payload

    def complete(self, system_prompt: str, user_text: str) -> LLMResponse:
        payload = self.build_payload(system_prompt, user_text)
        request = urllib.request.Request(
            self.settings.endpoint,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.settings.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.settings.timeout_seconds) as response:
                status = response.status
                body = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as error:
            detail = ""
            try:
                detail = _truncate(error.read().decode("utf-8", errors="replace"))
            except Exception:  # pragma: no cover - 读取错误体失败时不影响主错误
                detail = ""
            raise ParseTransportError(
                f"模型接口返回 HTTP {error.code}：{detail}",
                status_code=error.code,
            ) from error
        except (urllib.error.URLError, socket.timeout, TimeoutError) as error:
            raise ParseTransportError(f"模型调用失败：{error}") from error

        if status != 200:
            raise ParseTransportError(f"模型接口返回 HTTP {status}", status_code=status)

        try:
            data = json.loads(body)
        except json.JSONDecodeError as error:
            raise ParseTransportError(
                f"模型接口响应不是合法 JSON：{_truncate(body)}"
            ) from error

        try:
            message = data["choices"][0]["message"]
            text = message.get("content") or ""
        except (KeyError, IndexError, TypeError) as error:
            raise ParseTransportError(
                f"模型响应缺少 choices[0].message.content：{_truncate(body)}"
            ) from error

        extra: dict[str, Any] = {}
        if message.get("reasoning_content"):
            extra["has_reasoning_content"] = True
        if data.get("model"):
            extra["response_model"] = data["model"]
        return LLMResponse(
            text=text,
            model=data.get("model") or self.settings.model,
            usage=data.get("usage"),
            extra=extra,
        )


class MockChatClient:
    """离线固定响应客户端：按用户原话查表返回，不联网、不需要密钥。"""

    name = "mock"

    def __init__(self, responses: dict[str, str], model: str = "mock-qwen"):
        self.responses = responses
        self.model = model

    @classmethod
    def from_file(cls, path: Path, model: str = "mock-qwen") -> "MockChatClient":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("responses"), dict):
            raise ParseConfigError(f"mock 响应文件格式不正确：{path}")
        return cls(data["responses"], model=model)

    def complete(self, system_prompt: str, user_text: str) -> LLMResponse:
        if user_text not in self.responses:
            raise ParseConfigError(
                f"mock 响应文件中没有这条输入：{_truncate(user_text, 60)}",
                hint="mock 只用于离线验证流程；真实结果必须在配置密钥后重跑",
            )
        return LLMResponse(text=self.responses[user_text], model=self.model, usage=None)
