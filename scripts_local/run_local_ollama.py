"""本地 Ollama 跑评测：不改上游仓库代码，只在运行时把 client 工厂替换为本地适配器。

与 `python -m parsing.run_parse` 完全同一套流程（同一评分、同一报告、同一 jsonl 记录），
唯一差别是模型由本机 Ollama 提供（OpenAI 兼容 /v1/chat/completions）。

用法（项目根目录）：
    python scripts_local/run_local_ollama.py --model qwen2.5:7b-instruct-q4_k_m \
        --samples v2_eval/samples_v2.jsonl --splits dev,val \
        --out v2_eval/baseline/local_ollama_runs.jsonl \
        --report v2_eval/baseline/local_ollama_report.md --tag local
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from parsing.config import Settings  # noqa: E402
from parsing.llm_client import DashScopeChatClient  # noqa: E402
import parsing.parse_requirement as pr  # noqa: E402
import parsing.run_parse as rp  # noqa: E402


# 默认本机；若 Ollama 装在另一台机器（共享 GPU）可用环境变量覆盖
OLLAMA_BASE = os.environ.get("MOLING_OLLAMA_BASE", "http://127.0.0.1:11434/v1")

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _device  # noqa: E402  本地硬件快照，见 _device.py


def _device_snapshot() -> dict:
    """采集本机硬件，写进 `<out>.device.json`（上游记录里没有硬件字段）。"""
    return _device.snapshot()



class OllamaChatClient(DashScopeChatClient):
    """复用上游的请求构造/解析/重试逻辑，只把 endpoint 与鉴权换成 Ollama 本地服务。"""

    name = "ollama"

    def __init__(self, settings: Settings):
        self.settings = settings

    def build_payload(self, system_prompt: str, user_text: str) -> dict:
        payload = super().build_payload(system_prompt, user_text)
        # 本地服务不需要 api_key；num_ctx 给足以便容纳完整提示词
        payload.setdefault("options", {})
        return payload


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--model", required=True)
    # 可选：指定一份临时提示词文件做对照实验（不写进上游仓库，只在本进程内注册）
    parser.add_argument("--prompt-file", default=None)
    parser.add_argument("--prompt-version", default="v2")
    known, rest = parser.parse_known_args()
    model = known.model
    version = known.prompt_version
    if known.prompt_file:
        # 直接在 run_parse 的参数字里移除，避免 argparse 报未知参数
        rest = [a for a in rest if a != "--prompt-file" and a != known.prompt_file]

    os.environ["MOLING_LLM_BASE_URL"] = OLLAMA_BASE
    os.environ["MOLING_LLM_MODEL"] = model
    os.environ["MOLING_LLM_API_KEY"] = "ollama-local"  # 仅为通过 allow_network 检查，不发出
    os.environ["MOLING_LLM_PROMPT_VERSION"] = version
    os.environ["MOLING_LLM_TIMEOUT"] = "300"
    os.environ.pop("MOLING_LLM_EXTRA_BODY", None)  # 本地不需要 enable_thinking

    if known.prompt_file:
        # v2 走 parse_requirement_v2.PROMPT_PATH（独立常量），但模块里的函数直接用全局名，
        # eval_v2 只是 from-import 了它做哈希记录 → 改模块全局即可同时影响两者。
        import parsing.parse_requirement_v2 as pr2

        resolved = Path(known.prompt_file).resolve()
        pr2.PROMPT_PATH = resolved
        print(f"[local] 提示词覆盖：v2 -> {resolved}")

    # 硬件快照：上游记录没有硬件字段，靠它事后自证“这份结果跑在哪台机器上”
    device = _device_snapshot()
    print(f"[local] 硬件：{_device.one_line(device)}")
    out_path = Path(rest[rest.index("--out") + 1]) if "--out" in rest else None

    # 劫持 client 工厂与鉴权头
    # rp 已经 from ... import build_client 把函数对象绑到自己命名空间，两处都要换
    pr.build_client = lambda settings: OllamaChatClient(settings)
    rp.build_client = pr.build_client
    orig_complete = DashScopeChatClient.complete

    def complete(self, system_prompt, user_text):
        import json
        import socket
        import urllib.error
        import urllib.request

        payload = self.build_payload(system_prompt, user_text)
        request = urllib.request.Request(
            self.settings.endpoint,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.settings.timeout_seconds) as response:
                body = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as error:
            from parsing.errors import ParseTransportError

            detail = error.read().decode("utf-8", errors="replace")[:400]
            raise ParseTransportError(
                f"本地模型接口返回 HTTP {error.code}：{detail}", status_code=error.code
            ) from error
        except (urllib.error.URLError, socket.timeout, TimeoutError) as error:
            from parsing.errors import ParseTransportError

            raise ParseTransportError(f"本地模型调用失败：{error}") from error

        data = json.loads(body)
        try:
            message = data["choices"][0]["message"]
            text = message.get("content") or ""
        except (KeyError, IndexError, TypeError):
            from parsing.errors import ParseTransportError

            raise ParseTransportError(f"本地模型响应异常：{body[:400]}") from None

        from parsing.llm_client import LLMResponse

        extra = {"response_model": data.get("model")} if data.get("model") else {}
        return LLMResponse(text=text, model=data.get("model") or self.settings.model,
                           usage=data.get("usage"), extra=extra)

    OllamaChatClient.complete = complete
    _ = orig_complete

    sys.argv = [sys.argv[0]] + rest
    code = rp.main()

    # 注意：`run_parse` 返回 1 表示「有样本未通过」，不是崩溃——产物照样是完整的。
    # 早先这里写 `code == 0` 才落快照，结果 14B 那批（36/98 通过、exit=1）反而没留下硬件信息。
    if out_path is not None and out_path.exists() and out_path.stat().st_size > 0:
        import json

        side = out_path.with_suffix(".device.json")
        side.parent.mkdir(parents=True, exist_ok=True)
        side.write_text(json.dumps(device, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[local] 硬件快照已写入：{side}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
