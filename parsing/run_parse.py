"""批量跑解析样例，把每条输入、期望、实际结果、状态和失败原因写进 parse_runs.jsonl。

用法（在项目根目录）：

    python -m parsing.run_parse --client mock      # 无需密钥，验证流程
    python -m parsing.run_parse --client real      # 真实模型，需在 .env 配置密钥

默认读取 user_requirement/examples_v0.3.json（第 2 周 10 组样例），
默认写入 parsing/parse_runs.jsonl。退出码：0 全部符合期望，1 有不符合项，2 批次无法运行。
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):  # 支持 python parsing/run_parse.py 直接运行
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schemas import UserRequirement  # noqa: E402

from parsing.config import get_settings  # noqa: E402
from parsing.errors import ParseConfigError, ParseError  # noqa: E402
from parsing.llm_client import MockChatClient  # noqa: E402
from parsing.parse_requirement import PROTOCOL_FIELDS, build_client, parse_text  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SAMPLES = PROJECT_ROOT / "user_requirement" / "examples_v0.3.json"
DEFAULT_OUT = Path(__file__).resolve().parent / "parse_runs.jsonl"
DEFAULT_MOCK = Path(__file__).resolve().parent / "mock_responses.json"
MAX_RAW_CHARS = 2000


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--client", choices=("real", "mock"), default="real", help="调用真实模型或离线固定响应")
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES, help="样例文件（默认第 2 周 10 组）")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="运行记录输出路径")
    parser.add_argument("--mock-file", type=Path, default=DEFAULT_MOCK, help="离线固定响应文件")
    parser.add_argument("--limit", type=int, default=0, help="只跑前 N 条，0 表示全部")
    parser.add_argument(
        "--splits", default="",
        help="只跑指定分集，逗号分隔（如 dev,val）；先于封存检查生效，便于只跑开发/验证集",
    )
    parser.add_argument("--report", type=Path, default=None, help="把评测报告写到该 Markdown 文件")
    parser.add_argument("--tag", default="", help="批次标签，写进 batch_id")
    parser.add_argument("--append", action="store_true", help="追加到已有运行记录，而不是覆盖")
    parser.add_argument(
        "--allow-sealed",
        action="store_true",
        help="允许跑封存集；调提示词时必须保持关闭，封存集只用于最终评估",
    )
    return parser.parse_args(argv)


SEALED_MARKS = {"sealed", "test", "封存", "封存测试"}


def sealed_samples(samples: list[dict]) -> list[dict]:
    """按 W03-3 约定，split 标为封存的样本不允许在调提示词时运行。"""
    return [
        sample
        for sample in samples
        if str(sample.get("split", "")).strip().lower() in SEALED_MARKS
    ]


def load_samples(path: Path) -> list[dict]:
    """读取样例：JSON 数组或 JSONL（每行一条）都支持，按内容自动识别。"""
    text = path.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if stripped.startswith("["):
        data = json.loads(text)
    else:
        data = []
        for lineno, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ParseConfigError(f"第 {lineno} 行 JSON 解析失败：{error}") from error
    if not isinstance(data, list):
        raise ParseConfigError(f"样例文件必须是数组或 JSONL：{path}")
    samples = []
    for index, item in enumerate(data):
        if not isinstance(item, dict) or "input" not in item:
            raise ParseConfigError(f"第 {index + 1} 条样例缺少 input 字段：{path}")
        samples.append(item)
    return samples


def compare(expected: dict, actual: UserRequirement | None) -> tuple[list[str], str, bool]:
    """返回 (字段差异列表, follow_up 检查结论, 是否与期望一致)。"""
    if actual is None:
        return ["<无解析结果>"], "no_result", False
    actual_data = actual.model_dump()
    diff = [name for name in PROTOCOL_FIELDS if name != "follow_up" and actual_data[name] != expected.get(name)]

    expected_follow_up = expected.get("follow_up")
    actual_follow_up = actual_data["follow_up"]
    if expected_follow_up is None:
        follow_up_check = "present" if actual_follow_up is not None else "ok"
        if actual_follow_up is not None:
            diff.append("follow_up")
    elif actual_follow_up is None:
        follow_up_check = "missing"
        diff.append("follow_up")
    elif actual_follow_up == expected_follow_up:
        follow_up_check = "ok"
    else:
        follow_up_check = "text_differs"
    return diff, follow_up_check, not diff


def record_for(
    *,
    batch_id: str,
    sample: dict,
    outcome,
    error: ParseError | None,
    timestamp: str,
) -> dict:
    expected = sample.get("expected", {})
    actual = outcome.requirement if outcome else None
    diff, follow_up_check, matched = compare(expected, actual)

    if error is not None:
        result_status = f"{error.layer}_error"
        failure_reason = str(error)
    else:
        result_status = f"ok_{actual.status}"
        failure_reason = None

    usage = outcome.usage if outcome else None
    return {
        "run_id": uuid.uuid4().hex[:8],
        "batch_id": batch_id,
        "timestamp": timestamp,
        "sample_id": sample.get("id"),
        "category": sample.get("category"),
        "subtype": sample.get("subtype"),
        "split": sample.get("split"),
        "semantic_group": sample.get("semantic_group"),
        "plan_gate": sample.get("plan_gate"),
        "input": sample.get("input"),
        "expected": expected,
        "actual": actual.model_dump() if actual else None,
        "status": result_status,
        "failure_reason": failure_reason,
        "field_diff": diff,
        "follow_up_check": follow_up_check,
        "expectation_match": matched,
        "strict_match": matched and follow_up_check == "ok",
        "client": outcome.client if outcome else None,
        "mock": (outcome.client == "mock") if outcome else None,
        "model": outcome.model if outcome else None,
        "prompt_version": outcome.prompt_version if outcome else None,
        "prompt_sha256": outcome.prompt_sha256 if outcome else None,
        "temperature": outcome.temperature if outcome else None,
        "latency_ms": outcome.latency_ms if outcome else None,
        "attempts": outcome.attempts if outcome else 0,
        "usage": usage,
        "usage_missing": usage is None,
        "warnings": outcome.warnings if outcome else [],
        "missing_keys": outcome.missing_keys if outcome else [],
        "raw_text": (outcome.raw_text[:MAX_RAW_CHARS] + "…（已截断）") if outcome and len(outcome.raw_text) > MAX_RAW_CHARS else (outcome.raw_text if outcome else None),
        "error_layer": error.layer if error else None,
        "error_detail": (
            {"status_code": getattr(error, "status_code", None), "hint": getattr(error, "hint", None)}
            if error
            else None
        ),
    }


def _rate(hit: int, total: int) -> str:
    return f"{hit}/{total}（{hit / total:.1%}）" if total else f"{hit}/{total}（—）"


def _bucket_table(records: list[dict], key: str, title: str, note: str = "") -> list[str]:
    groups: dict[str, list[dict]] = {}
    for record in records:
        if key == "plan_gate":
            gate = (record.get("plan_gate") or {}).get("gate") or "无标记"
            if gate == "block" and (record.get("plan_gate") or {}).get("layer_conflict"):
                gate = "block（两层冲突）"
        else:
            gate = record.get(key) or "未标注"
        groups.setdefault(str(gate), []).append(record)
    lines = [f"### {title}", "", "| 分桶 | 条数 | 完全一致（9 字段+状态） | 追问措辞逐字一致 |", "|---|---:|---|---|"]
    for name in sorted(groups):
        rows = groups[name]
        match = sum(1 for r in rows if r["expectation_match"])
        strict = sum(1 for r in rows if r["strict_match"])
        lines.append(f"| {name} | {len(rows)} | {_rate(match, len(rows))} | {_rate(strict, len(rows))} |")
    if note:
        lines += ["", f"> {note}"]
    lines.append("")
    return lines


def summarize(
    records: list[dict],
    *,
    batch_id: str,
    model: str | None,
    prompt_version: str | None,
    prompt_sha256: str | None,
    client_name: str,
    samples_path: str,
) -> str:
    """生成评测报告：分集/类型/规划侧门禁分桶 + 字段级准确率 + 失败清单。

    - 字段准确率的分母是该字段有标注的样本数；空值判定按“命中 null”计。
    - `plan_gate=block` 的样本是规划侧契约边界，单独成桶，不计入“模型理解错误”。
    """
    total = len(records)
    matched = sum(1 for r in records if r["expectation_match"])
    latencies = sorted(r["latency_ms"] for r in records if r.get("latency_ms"))
    tokens = [r["usage"]["total_tokens"] for r in records if r.get("usage") and "total_tokens" in r["usage"]]
    failures = [r for r in records if not r["expectation_match"]]

    lines = [
        "# 需求解析评测报告（W03-1 解析模块）",
        "",
        f"- 批次：`{batch_id}`",
        f"- 样例：`{samples_path}`（{total} 条）",
        f"- 调用：client=`{client_name}`，model=`{model}`，提示词 `{prompt_version}`（sha256 `{prompt_sha256}`）",
        f"- 完全一致：**{_rate(matched, total)}**（9 个字段 + status 全对）",
        f"- 耗时：{f'{latencies[0]}–{latencies[-1]} ms，中位 {latencies[len(latencies) // 2]} ms' if latencies else '无'}；"
        f"用量：{f'total_tokens {min(tokens)}–{max(tokens)}' if tokens else '未提供'}",
        "",
    ]
    if client_name == "mock":
        lines += ["> ⚠️ 本报告使用 mock 固定响应，只能验证流程，不能作为模型效果证据。", ""]

    lines += _bucket_table(records, "split", "按分集")
    lines += _bucket_table(records, "category", "按样本类型")
    lines += _bucket_table(
        records, "plan_gate", "按规划侧门禁",
        "`block` 表示需求已解析正确但规划侧仍会拒绝（非标准时长、非空 exclusions 等），"
        "属契约边界，不计入模型理解错误；`block（两层冲突）` 即需求侧 complete 却被拦截。",
    )

    # 字段级准确率
    lines += ["### 字段级准确率", "",
              "| 字段 | 一致 / 分母 | 准确率 |", "|---|---:|---|"]
    for field in PROTOCOL_FIELDS:
        comparable = [r for r in records if r.get("actual") is not None]
        if field == "follow_up":
            if not comparable:
                lines.append("| follow_up | 0 / 0 | — |")
                continue
            hit = sum(1 for r in comparable if r["follow_up_check"] == "ok")
            loose = sum(1 for r in comparable if r["follow_up_check"] in ("ok", "text_differs"))
            lines.append(
                f"| follow_up（逐字） | {hit} / {len(comparable)} | {_rate(hit, len(comparable))} |"
            )
            lines.append(
                f"| follow_up（仅要求“该问就问”） | {loose} / {len(comparable)} | {_rate(loose, len(comparable))} |"
            )
            continue
        hit = sum(1 for r in comparable if (r["actual"] or {}).get(field) == (r["expected"] or {}).get(field))
        lines.append(f"| {field} | {hit} / {len(comparable)} | {_rate(hit, len(comparable))} |")
    lines += ["", "> 字段级分母 = 成功解析的样本数；解析失败（config/transport/format）只出现在失败清单里，不摊进字段分母。", ""]

    # 失败清单：全部列出，不"豁免"任何一条；再单独标注两层判定边界样本的通过情况
    lines += ["### 失败清单（全部）", "",
              "| 编号 | 分集 | 类型 | 规划侧 | 输入 | 原因 | 期望 | 实际 |",
              "|---|---|---|---|---|---|---|---|"]
    if not failures:
        lines.append("| — | — | — | — | — | 无失败 | — | — |")
    for r in failures:
        if r.get("error_layer"):
            reason = f"解析失败（{r['error_layer']}）"
        else:
            reason = "字段/状态不一致：" + "、".join(r["field_diff"])
        gate = (r.get("plan_gate") or {}).get("gate") or "—"
        if gate == "block" and (r.get("plan_gate") or {}).get("layer_conflict"):
            gate = "block❗"
        if r.get("error_layer"):
            exp_cell = act_cell = "—"
        else:
            exp = {k: (r["expected"] or {}).get(k) for k in r["field_diff"]}
            act = {k: (r["actual"] or {}).get(k) for k in r["field_diff"]}
            exp_cell = f"`{json.dumps(exp, ensure_ascii=False)}`"
            act_cell = f"`{json.dumps(act, ensure_ascii=False)}`"
        lines.append(
            f"| {r['sample_id']} | {r.get('split')} | {r.get('category')} | {gate} | {r['input']} | "
            f"{reason} | {exp_cell} | {act_cell} |"
        )
    lines.append("")

    boundary = [r for r in records if (r.get("plan_gate") or {}).get("layer_conflict")]
    if boundary:
        ok = sum(1 for r in boundary if r["expectation_match"])
        lines += [f"### 两层判定边界样本（需求侧 complete / 规划侧 block，{len(boundary)} 条）", "",
                  f"本批一致 {ok}/{len(boundary)}。这批样本下游若把规划侧 422 计成模型理解错误，"
                  "基线会被压低约 16 个百分点（见 W03-3 `校验报告.md` 第五节），故在分桶表中单列。", "",
                  "| 编号 | 分集 | 本批是否一致 | 规划侧拦截原因 |", "|---|---|---|---|"]
        for r in boundary:
            lines.append(f"| {r['sample_id']} | {r.get('split')} | "
                         f"{'✅' if r['expectation_match'] else '❌'} | "
                         f"{(r.get('plan_gate') or {}).get('reason')} |")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        samples = load_samples(args.samples)
    except (OSError, json.JSONDecodeError, ParseConfigError) as error:
        print(f"无法读取样例：{error}", file=sys.stderr)
        return 2
    if args.splits:
        wanted = {item.strip().lower() for item in args.splits.split(",") if item.strip()}
        kept = [s for s in samples if str(s.get("split", "")).strip().lower() in wanted]
        if not kept:
            print(f"没有样例落在 --splits={args.splits} 指定的分集里。", file=sys.stderr)
            return 2
        print(f"按 --splits={args.splits} 过滤：{len(samples)} → {len(kept)} 条", file=sys.stderr)
        samples = kept
    if args.limit:
        samples = samples[: args.limit]

    if not args.allow_sealed:
        blocked = sealed_samples(samples)
        if blocked:
            print(
                f"样例中含 {len(blocked)} 条封存样本，调提示词阶段禁止运行；"
                "如确为最终评估，请加 --allow-sealed。",
                file=sys.stderr,
            )
            return 2

    settings, settings_warnings = get_settings()
    for warning in settings_warnings:
        print(f"配置警告：{warning}", file=sys.stderr)

    client = None
    if args.client == "mock":
        try:
            client = MockChatClient.from_file(args.mock_file)
        except (OSError, json.JSONDecodeError, ParseConfigError) as error:
            print(f"无法读取 mock 响应文件：{error}", file=sys.stderr)
            return 2
    else:
        try:
            client = build_client(settings)
        except ParseConfigError as error:
            print(f"无法开始真实调用：{error}", file=sys.stderr)
            if error.hint:
                print(f"提示：{error.hint}", file=sys.stderr)
            print("可先运行 python -m parsing.run_parse --client mock 验证流程。", file=sys.stderr)
            return 2

    batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + (f"-{args.tag}" if args.tag else "")
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    records: list[dict] = []
    matched_count = 0
    result_counts: dict[str, int] = {}

    for sample in samples:
        outcome = None
        error: ParseError | None = None
        try:
            outcome = parse_text(sample["input"], client=client, settings=settings)
        except ParseError as caught:
            error = caught
        record = record_for(
            batch_id=batch_id, sample=sample, outcome=outcome, error=error, timestamp=timestamp
        )
        records.append(record)
        result_counts[record["status"]] = result_counts.get(record["status"], 0) + 1
        if record["expectation_match"]:
            matched_count += 1
        mark = "符合" if record["expectation_match"] else "不符合"
        note = ""
        if error is not None:
            note = f" | {error.layer}: {error}"
        elif record["follow_up_check"] == "text_differs":
            note = " | 追问措辞与期望不同（内容等价）"
        print(f"{record['sample_id']} {record['status']} {mark}{note}")

    mode = args.out.open("a" if args.append else "w", encoding="utf-8")
    with mode as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    print()
    if args.client == "mock":
        print("注意：本批次使用 mock 固定响应，只能证明流程可跑，不能作为真实模型效果证据。")
    print(f"批次 {batch_id}：{matched_count}/{len(records)} 条与人工期望一致")
    print("状态分布：" + "，".join(f"{key} {value}" for key, value in sorted(result_counts.items())))
    print(f"运行记录：{args.out}")

    report = summarize(
        records,
        batch_id=batch_id,
        model=records[0]["model"] if records else None,
        prompt_version=records[0]["prompt_version"] if records else None,
        prompt_sha256=records[0]["prompt_sha256"] if records else None,
        client_name=args.client,
        samples_path=str(args.samples),
    )
    print()
    print(report)
    if args.report:
        args.report.write_text(report + "\n", encoding="utf-8")
        print(f"评测报告：{args.report}")
    return 0 if matched_count == len(records) and records else 1


if __name__ == "__main__":
    raise SystemExit(main())
