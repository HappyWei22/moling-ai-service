"""输入一句自然语言，打印解析出的需求 JSON。

用法（在项目根目录、已激活虚拟环境）：

    python try_parse.py "我是老师，每天练15分钟，想练楷书。"
    python try_parse.py                    # 不带参数则交互式输入
    python try_parse.py --version v1 "..." # 验证旧版协议
    python try_parse.py --mock "..."       # 离线固定响应，仅用于验证流程

默认使用 v2 解析和本地汇总追问，调用 .env 中配置的真实模型；只看 JSON 时请用管道或重定向区分诊断信息：

    python try_parse.py "..." 2>/dev/null
"""

from __future__ import annotations

import argparse
import json
from time import perf_counter
import sys

from parsing.errors import ParseConfigError, ParseError, ParseFormatError
from parsing.parse_requirement import extract_json_object, parse_text
from parsing.parse_requirement_v2 import parse_text_v2
from requirement_rules import RequirementNotReadyError, check_requirement_ready


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("text", nargs="*", help="用户原话；省略则交互式输入")
    parser.add_argument("--version", choices=("v1", "v2"), default="v2", help="解析协议版本，默认 v2")
    parser.add_argument("--mock", action="store_true", help="使用离线固定响应，不调用真实模型")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    text = " ".join(args.text).strip()
    if not text:
        try:
            text = input("请输入一句练字需求，例如“我是老师，每天练15分钟，想练楷书。”：").strip()
        except EOFError:
            text = ""
    if not text:
        print("没有输入内容。", file=sys.stderr)
        return 2

    client = None
    if args.mock:
        from parsing.llm_client import MockChatClient
        from parsing.run_parse import DEFAULT_MOCK

        client = MockChatClient.from_file(DEFAULT_MOCK)
        if args.version == "v2":
            # 复用旧版固定样例，但转换成 v2 模型候选协议。
            responses = {}
            for text_key, raw in client.responses.items():
                try:
                    candidate = extract_json_object(raw)
                except ParseFormatError:
                    responses[text_key] = raw
                    continue
                candidate["font"] = candidate.pop("style", None)
                for field in ("goal", "exclusions", "follow_up"):
                    candidate.pop(field, None)
                for error in candidate.get("errors", []):
                    if error.get("field") == "style":
                        error["field"] = "font"
                responses[text_key] = json.dumps(candidate, ensure_ascii=False)
            client = MockChatClient(responses, model=client.model)

    try:
        started = perf_counter()
        outcome = (parse_text_v2 if args.version == "v2" else parse_text)(text, client=client)
        latency_ms = round((perf_counter() - started) * 1000)
    except ParseConfigError as error:
        print(f"配置问题：{error}", file=sys.stderr)
        if error.hint:
            print(f"提示：{error.hint}", file=sys.stderr)
        if args.mock:
            print("提示：--mock 只认识 mock_responses.json 里的 10 条固定输入。", file=sys.stderr)
        return 2
    except ParseError as error:
        print(f"解析失败（{error.layer} 层）：{error}", file=sys.stderr)
        if error.layer == "transport":
            print("提示：检查 .env 的密钥、模型名和额度；这条失败没有被当成需求结果。", file=sys.stderr)
        return 1

    requirement = outcome.requirement
    if args.version == "v2":
        from main import ParseV2Response

        complete = requirement.status == "complete"
        result = ParseV2Response(code=0 if complete else 400, message=outcome.message,
                                 data=requirement if complete else None)
        print(result.model_dump_json(indent=2))
    else:
        print(requirement.model_dump_json(indent=2))

    # 诊断信息走 stderr，方便用 2>/dev/null 只取 JSON。
    print(
        f"# 模型 {outcome.model}｜提示词 {args.version if args.version == "v2" else outcome.prompt_version}({outcome.prompt_sha256})"
        f"｜{latency_ms} ms｜状态 {requirement.status}"
        f"{'（离线固定响应）' if outcome.client == 'mock' else ''}",
        file=sys.stderr,
    )
    for warning in getattr(outcome, "warnings", []):
        print(f"# 本地处理：{warning}", file=sys.stderr)

    if args.version == "v2":
        if requirement.status == "complete":
            print("# 该结果满足生成条件，可将 data 提交 POST /plan/v2", file=sys.stderr)
        else:
            print(f"# 该结果不能直接生成计划：当前状态 {requirement.status}", file=sys.stderr)
        return 0

    try:
        check_requirement_ready(requirement)
    except RequirementNotReadyError as error:
        print(f"# 该结果不能直接生成计划：{error}", file=sys.stderr)
    else:
        print("# 该结果满足生成条件，可直接提交 POST /plan", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
