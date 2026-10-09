"""v2 批量评测。由 run_parse --protocol v2 调用，语义追问另需人工复核。"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from schemas import ParsedRequirementV2
from parsing.config import get_settings
from parsing.errors import ParseConfigError, ParseError
from parsing.llm_client import DashScopeChatClient, MockChatClient
from parsing.parse_requirement_v2 import PROMPT_PATH, parse_text_v2

FIELDS = ("occupation", "scene", "font", "duration_minutes", "status")
TYPES = {"missing_field", "invalid_value", "conflicting_values"}
ISSUE_FIELDS = {"occupation", "scene", "font", "duration_minutes", "personalization"}


def issue_keys(issues):
    return {(item["type"], item["field"]) for item in issues}


def validate_samples(samples):
    """拒绝旧结构、错误答案与跨集组/会话，不能把缺标当作 null。"""
    ids, groups, conversations, inputs = set(), {}, {}, {}
    for sample in samples:
        sid = sample.get("id")
        try:
            if not isinstance(sid, str) or not sid or sid in ids:
                raise ValueError("id 缺失或重复")
            ids.add(sid)
            if sample.get("protocol_version") != "v2":
                raise ValueError("protocol_version 必须为 v2")
            if sample.get("split") not in {"dev", "val", "sealed"}:
                raise ValueError("split 必须为 dev/val/sealed")
            if not isinstance(sample["input"], str) or not sample["input"].strip():
                raise ValueError("input 必须为非空文本")
            if inputs.setdefault(sample["input"].strip(), sample["split"]) != sample["split"]:
                raise ValueError("完全相同的输入跨分集")
            if not isinstance(sample.get("tags", []), list) or not all(isinstance(t, str) for t in sample.get("tags", [])):
                raise ValueError("tags 必须为字符串列表")
            if sample.get("source") is not None and not isinstance(sample["source"], dict):
                raise ValueError("source 必须为对象")
            if sample.get("conversation_id") is not None and not isinstance(sample["conversation_id"], str):
                raise ValueError("conversation_id 必须为字符串或 null")
            group = sample.get("semantic_group")
            if not isinstance(group, str) or not group:
                raise ValueError("semantic_group 必须为非空字符串")
            for mapping, key in ((groups, group), (conversations, sample.get("conversation_id"))):
                if key is not None:
                    if mapping.setdefault(key, sample["split"]) != sample["split"]:
                        raise ValueError("同语义组或会话跨分集")
            expected = sample["expected_requirement"]
            if set(expected) != set(FIELDS):
                raise ValueError("expected_requirement 必须且只能含 v2 五字段")
            ParsedRequirementV2.model_validate(expected)
            if expected["duration_minutes"] not in (None, 5, 15, 30):
                raise ValueError("标准答案时长只能为 null/5/15/30")
            for name in ("expected_model_errors", "expected_issues"):
                items = sample[name]
                if not isinstance(items, list):
                    raise ValueError(f"{name} 必须为列表")
                for item in items:
                    if not isinstance(item, dict) or set(item) != {"type", "field", "value"}:
                        raise ValueError(f"{name} 问题必须包含 type/field/value")
                    if item["type"] not in TYPES or item["field"] not in ISSUE_FIELDS:
                        raise ValueError("问题类型或字段非法")
                    if name == "expected_model_errors" and item["type"] == "missing_field":
                        raise ValueError("模型错误标注不能包含本地缺失问题")
                if len(issue_keys(items)) != len(items):
                    raise ValueError("同类型同字段的问题重复")
            issues = sample["expected_issues"]
            semantic = [i for i in issues if i["type"] != "missing_field"]
            if semantic != sample["expected_model_errors"]:
                # 忽略问题列表顺序，原值必须保持一致。
                canon = lambda xs: sorted(json.dumps(i, sort_keys=True, ensure_ascii=False) for i in xs)
                if canon(semantic) != canon(sample["expected_model_errors"]):
                    raise ValueError("模型错误与最终问题集合不一致")
            for item in semantic:
                if item["field"] in expected and expected[item["field"]] is not None:
                    raise ValueError("非法或冲突字段必须置空")
            missing = set()
            for f in ("font", "duration_minutes"):
                if expected[f] is None and not any(i["field"] == f for i in semantic):
                    missing.add(("missing_field", f))
            if expected["occupation"] is None and expected["scene"] is None and not any(
                i["field"] in {"occupation", "scene", "personalization"} for i in semantic
            ):
                missing.add(("missing_field", "personalization"))
            if issue_keys([i for i in issues if i["type"] == "missing_field"]) != missing:
                raise ValueError("缺失问题不完整或重复报告非法/冲突字段")
            types = {i["type"] for i in issues}
            status = ("invalid" if "invalid_value" in types else "conflict" if "conflicting_values" in types
                      else "needs_clarification" if issues else "complete")
            if expected["status"] != status:
                raise ValueError("状态与问题集合不一致")
            api = sample["expected_api"]
            complete = status == "complete"
            if api.get("http_status") != 200 or api.get("code") != (0 if complete else 400):
                raise ValueError("业务 API 状态码不一致")
            if "data" not in api or api["data"] != (expected if complete else None):
                raise ValueError("expected_api.data 与完成状态不一致")
            if complete and api.get("message") != "ok":
                raise ValueError("完成样本的 expected_api.message 必须为 ok")
            if set(api) - {"http_status", "code", "data", "message"}:
                raise ValueError("expected_api 存在未知字段")
            check = sample.get("message_check", {})
            if not isinstance(check, dict) or set(check) - {"required", "forbidden", "contains", "not_contains"}:
                raise ValueError("message_check 字段非法")
            for values in check.values():
                if not isinstance(values, list) or not all(isinstance(v, str) and v for v in values):
                    raise ValueError("message_check 各项必须为非空字符串列表")
        except (ValueError, KeyError, TypeError) as error:
            raise ParseConfigError(f"样本 {sid!r} 标注不合法：{error}") from error


def evaluate(sample, outcome, error):
    expected = sample["expected_requirement"]
    actual = outcome.requirement.model_dump() if outcome else None
    issues = outcome.issues if outcome else []
    model_errors = outcome.candidate.get("errors") if outcome else None
    model_valid = isinstance(model_errors, list) and all(
        isinstance(i, dict) and isinstance(i.get("type"), str) and isinstance(i.get("field"), str)
        for i in model_errors
    )
    model_keys = issue_keys(model_errors) if model_valid else set()
    wanted_model = issue_keys(sample["expected_model_errors"])
    wanted = issue_keys(sample["expected_issues"])
    got = issue_keys(issues)
    diff = [f for f in FIELDS if actual is None or actual[f] != expected[f]]
    complete = actual is not None and actual["status"] == "complete"
    api = {"http_status": 200, "code": 0 if complete else 400,
           "data": actual if complete else None, "message": outcome.message} if outcome else None
    api_match = api is not None and all(api[k] == v for k, v in sample["expected_api"].items())
    message = outcome.message if outcome else ""
    check = sample.get("message_check", {})
    literal_match = (all(s in message for s in check.get("contains", [])) and
                     all(s not in message for s in check.get("not_contains", [])))
    # required/forbidden 是人工语义要求，不拿中文说明做子串匹配。
    message_review = "not_needed" if complete and expected["status"] == "complete" else "pending"
    value_match = model_valid and all(any(
        got_item.get("type") == item["type"] and got_item.get("field") == item["field"]
        and got_item.get("value") == item["value"] for got_item in model_errors
    ) for item in sample["expected_model_errors"])
    model_match = model_valid and model_keys == wanted_model and value_match and len(model_errors) == len(model_keys)
    raw_contract = outcome is not None and set(outcome.candidate) == set(FIELDS) | {"errors"}
    model_status_match = outcome is not None and outcome.candidate.get("status") == expected["status"]
    auto_match = (error is None and not diff and got == wanted and len(issues) == len(got)
                  and api_match and literal_match and model_match and raw_contract and model_status_match)
    return {
        "sample_id": sample["id"], "protocol_version": "v2", "split": sample["split"],
        "semantic_group": sample["semantic_group"], "conversation_id": sample.get("conversation_id"),
        "tags": sample.get("tags", []), "source": sample.get("source"), "input": sample["input"],
        "expected": expected, "actual": actual, "field_diff": diff,
        "expected_issues": sample["expected_issues"], "actual_issues": issues,
        "issues_match": outcome is not None and got == wanted and len(issues) == len(got),
        "missing_issues": sorted(wanted - got), "extra_issues": sorted(got - wanted),
        "model_errors": model_errors, "model_errors_match": model_match,
        "model_error_hits": len(model_keys & wanted_model), "model_error_expected": len(wanted_model),
        "model_error_actual": len(model_keys), "model_values_match": value_match,
        "raw_contract_match": raw_contract, "actual_api": api, "api_match": api_match,
        "model_status_match": model_status_match,
        "message_check": check, "message_literal_match": literal_match, "message_review": message_review,
        "automated_match": auto_match,
        "end_to_end_match": (False if not auto_match else True if message_review == "not_needed" else None),
        "wrong_release": expected["status"] != "complete" and complete,
        "error_layer": error.layer if error else None, "failure_reason": str(error) if error else None,
        "raw_text": outcome.raw_text if outcome else getattr(error, "raw_text", ""),
        "client": outcome.client if outcome else None, "model": outcome.model if outcome else None,
        "latency_ms": outcome.latency_ms if outcome else None, "usage": outcome.usage if outcome else None,
    }


def rate(hit, total):
    return f"{hit}/{total}（{hit / total:.1%}）" if total else "0/0（无可比样本）"


def summarize(records, metadata):
    lines = ["# v2 需求解析评测报告", "", f"- 批次：`{metadata['batch_id']}`",
             f"- 样本 SHA256：`{metadata['samples_sha256']}`",
             f"- 模型：`{metadata['model']}`；提示词 SHA256：`{metadata['prompt_sha256']}`",
             f"- 调用：`{metadata['client']}`；代码提交：`{metadata['code_commit']}`",
             "", "> 本报告的 API 比较由解析结果构造，未发起 HTTP 请求；真实 HTTP 契约另由接口测试验证。",
             "> 自动检查不等于追问语义验收；pending 项需人工检查 required/forbidden，并统计漏问、重复问、多余问。", ""]
    if metadata["client"] == "mock":
        lines += ["> 本批使用 mock 固定响应，只验证评测流程，不是模型效果证据。", ""]
    for split in sorted({r["split"] for r in records}):
        rows = [r for r in records if r["split"] == split]
        valid = [r for r in rows if r["actual"] is not None]
        negative = [r for r in rows if r["expected"]["status"] != "complete"]
        pending = sum(r["end_to_end_match"] is None for r in rows)
        lines += [f"## {split}" + ("：封存集一次性最终评估" if split == "sealed" else ""), "",
                  f"- 输入 {len(rows)} 条；语义组 {len({r['semantic_group'] for r in rows})}；独立会话 {len({r['conversation_id'] for r in rows if r['conversation_id']})}。",
                  f"- 自动检查全部一致：{rate(sum(r['automated_match'] for r in rows), len(rows))}",
                  f"- 完整问题集合一致：{rate(sum(r['issues_match'] for r in rows), len(rows))}",
                  f"- 错误放行率：{rate(sum(r['wrong_release'] for r in negative), len(negative))}",
                  f"- 模型错误召回率：{rate(sum(r['model_error_hits'] for r in valid), sum(r['model_error_expected'] for r in valid))}",
                  f"- 模型错误精确率：{rate(sum(r['model_error_hits'] for r in valid), sum(r['model_error_actual'] for r in valid))}",
                  f"- 技术失败：{dict(Counter(r['error_layer'] for r in rows if r['error_layer']))}",
                  f"- 端到端已确认成功：{rate(sum(r['end_to_end_match'] is True for r in rows), len(rows))}；语义待复核 {pending} 条（未复核不能作为最终成功率）。",
                  "", "| 字段 | 成功解析样本准确率 | 非空答案准确率 |", "|---|---|---|"]
        for f in FIELDS:
            nonnull = [r for r in valid if r["expected"][f] is not None]
            lines.append(f"| {f} | {rate(sum(r['actual'][f] == r['expected'][f] for r in valid), len(valid))} | {rate(sum(r['actual'][f] == r['expected'][f] for r in nonnull), len(nonnull))} |")
        lines += ["", "| 分桶 | 自动一致 / 全部（包含技术失败） |", "|---|---|"]
        buckets = {}
        for r in rows:
            keys = [f"status:{r['expected']['status']}", f"source:{(r.get('source') or {}).get('kind', '未标注')}"]
            keys += [f"tag:{t}" for t in r["tags"]]
            for key in keys:
                buckets.setdefault(key, []).append(r)
        for key, bucket in sorted(buckets.items()):
            lines.append(f"| {key} | {rate(sum(r['automated_match'] for r in bucket), len(bucket))} |")
        lines += ["", "### 自动检查失败与语义复核清单", ""]
        for r in rows:
            if not r["automated_match"] or r["message_review"] == "pending":
                detail = {k: r[k] for k in ("field_diff", "missing_issues", "extra_issues", "model_errors_match", "model_status_match", "raw_contract_match", "api_match", "message_literal_match", "message_review", "failure_reason")}
                lines += [f"- `{r['sample_id']}`：`{json.dumps(detail, ensure_ascii=False)}`"]
        lines.append("")
    return "\n".join(lines)


def main_v2(args):
    from parsing.run_parse import DEFAULT_SAMPLES, DEFAULT_MOCK, DEFAULT_OUT, load_samples, sealed_samples
    try:
        if args.samples == DEFAULT_SAMPLES:
            raise ParseConfigError("v2 必须用 --samples 指定正式 v2 样本，不能默认读取 v1 样例")
        samples = load_samples(args.samples)
        # 验证跨集隔离后再过滤，不读取配置、不调用模型。
        validate_samples(samples)
        if args.splits:
            wanted = {s.strip().lower() for s in args.splits.split(",") if s.strip()}
            samples = [s for s in samples if s["split"] in wanted]
        if not samples:
            raise ParseConfigError("没有可运行样本")
        if args.limit < 0:
            raise ParseConfigError("--limit 不能为负数")
        sealed = sealed_samples(samples)
        if sealed and not args.allow_sealed:
            raise ParseConfigError("含封存样本，禁止运行；已获最终评估授权才可加 --allow-sealed")
        if sealed and (args.limit or args.append):
            raise ParseConfigError("封存评测不允许 --limit 或 --append，须整批一次运行")
        if args.limit:
            samples = samples[:args.limit]
        if args.client == "mock" and args.mock_file == DEFAULT_MOCK:
            raise ParseConfigError("v2 mock 必须用 --mock-file 指定 v2 六字段模型响应文件")
        if args.out == DEFAULT_OUT:
            args.out = DEFAULT_OUT.with_name("parse_runs_v2.jsonl")
        settings, warnings = get_settings()
        for warning in warnings:
            print(f"配置警告：{warning}", file=sys.stderr)
        client = MockChatClient.from_file(args.mock_file) if args.client == "mock" else DashScopeChatClient(settings)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
    except (OSError, ValueError, ParseError) as error:
        print(f"无法开始 v2 评测：{error}", file=sys.stderr)
        return 2
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        revision = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True).stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        revision, dirty = None, None
    metadata = {"batch_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + (f"-{args.tag}" if args.tag else ""),
                "timestamp": timestamp, "samples_path": str(args.samples),
                "samples_sha256": hashlib.sha256(args.samples.read_bytes()).hexdigest(),
                "prompt_version": "v2", "prompt_sha256": hashlib.sha256(PROMPT_PATH.read_bytes()).hexdigest(),
                "model": settings.model if args.client == "real" else client.model,
                "temperature": settings.temperature, "timeout_seconds": settings.timeout_seconds,
                "extra_body": settings.extra_body, "client": args.client, "code_commit": revision,
                "code_dirty": dirty, "command": sys.argv if args is not None else [],
                "evaluator_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "parser_code_sha256": hashlib.sha256(PROMPT_PATH.with_name("parse_requirement_v2.py").read_bytes()).hexdigest()}
    records = []
    with args.out.open("a" if args.append else "w", encoding="utf-8") as handle:
        for sample in samples:
            outcome, error = None, None
            try:
                outcome = parse_text_v2(sample["input"], client=client, settings=settings)
            except ParseError as caught:
                error = caught
            record = evaluate(sample, outcome, error)
            record.update(metadata)
            # 响应中的实际模型名称优先于请求配置。
            record["model"] = outcome.model if outcome else metadata["model"]
            records.append(record)
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            print(f"{sample['id']}：{'自动符合' if record['automated_match'] else '不符合'}；追问语义 {record['message_review']}")
    report = summarize(records, metadata)
    print(report)
    if args.report:
        args.report.write_text(report + "\n", encoding="utf-8")
    return 0 if all(r["automated_match"] for r in records) else 1
