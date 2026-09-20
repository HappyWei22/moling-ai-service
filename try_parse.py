"""输入一句自然语言，打印解析出的需求 JSON。

用法（在项目根目录、已激活虚拟环境）：

    python try_parse.py "我是老师，每天练15分钟，想练楷书。"
    python try_parse.py                    # 不带参数则交互式输入
    python try_parse.py --mock "..."       # 离线固定响应，仅用于验证流程

默认调用 .env 中配置的真实模型；只看 JSON 时请用管道或重定向区分诊断信息：

    python try_parse.py "..." 2>/dev/null
"""

from __future__ import annotations

import argparse
import sys

from parsing.errors import ParseConfigError, ParseError
from parsing.parse_requirement import parse_text
from requirement_rules import RequirementNotReadyError, check_requirement_ready


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("text", nargs="*", help="用户原话；省略则交互式输入")
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

    try:
        outcome = parse_text(text, client=client)
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
    print(requirement.model_dump_json(indent=2))

    # 诊断信息走 stderr，方便用 2>/dev/null 只取 JSON。
    print(
        f"# 模型 {outcome.model}｜提示词 {outcome.prompt_version}({outcome.prompt_sha256})"
        f"｜{outcome.latency_ms} ms｜状态 {requirement.status}"
        f"{'（离线固定响应）' if outcome.client == 'mock' else ''}",
        file=sys.stderr,
    )
    for warning in outcome.warnings:
        print(f"# 本地处理：{warning}", file=sys.stderr)

    try:
        check_requirement_ready(requirement)
    except RequirementNotReadyError as error:
        print(f"# 该结果不能直接生成计划：{error}", file=sys.stderr)
    else:
        print("# 该结果满足生成条件，可直接提交 POST /plan", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
