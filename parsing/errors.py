"""解析模块的异常类型。

区分失败发生在哪一层，便于记录失败样例并让第 4 周按层修复：

- ParseConfigError：本地配置缺失或非法，请求还没有发出去
- ParseTransportError：请求发出后失败（网络、超时、HTTP 状态码、响应不是 JSON）
- ParseFormatError：拿到模型文本，但不是可用的需求 JSON
"""

from __future__ import annotations


class ParseError(Exception):
    """解析失败的基类，附带可写入运行记录的层名。"""

    layer = "unknown"


class ParseConfigError(ParseError):
    layer = "config"

    def __init__(self, message: str, hint: str | None = None):
        super().__init__(message)
        self.hint = hint


class ParseTransportError(ParseError):
    layer = "transport"

    def __init__(self, message: str, *, status_code: int | None = None, attempts: int = 1):
        super().__init__(message)
        self.status_code = status_code
        self.attempts = attempts


class ParseFormatError(ParseError):
    layer = "format"

    def __init__(self, message: str, *, raw_text: str = "", missing_keys: list[str] | None = None):
        super().__init__(message)
        self.raw_text = raw_text
        self.missing_keys = missing_keys or []
