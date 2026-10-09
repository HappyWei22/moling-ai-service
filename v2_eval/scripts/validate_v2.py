"""v2 评测集建集校验：数量配额、覆盖度、分集隔离、近重复、清单哈希。

上游 parsing/eval_v2.validate_samples 只验结构一致性；本脚本补足第 5、7 节要求的
数量与覆盖配额、近重复检测、清单与哈希，并产出可提交的校验报告。
"""

from __future__ import annotations

import collections
import difflib
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from parsing.eval_v2 import validate_samples  # noqa: E402

SAMPLES = ROOT / "v2_eval" / "samples_v2.jsonl"
MANIFEST = ROOT / "v2_eval" / "split_manifest.json"
REPORT = ROOT / "v2_eval" / "校验报告.md"

# 第 5 节最低配额
MIN_TOTAL = 100
MIN_CONFLICT = 6
MIN_MULTI_ISSUE = 15
MIN_MULTI_TURN_POINTS = 20
MIN_MULTI_TURN_SESSIONS = 8
MIN_NO_INFERENCE = 6


def has_tag(row, *names):
    return any(name in row["tags"] for name in names)


def coverage(namespace, wanted, predicate):
    """namespace 提供别名映射，wanted 是需全覆盖的取值集合。"""
    seen = set()
    for row in rows_of(namespace):
        if predicate(row):
            for key, values in wanted.items():
                got = row["expected_requirement"].get(key)
                if got in values:
                    seen.add((key, got))
    return seen


def main() -> int:
    rows = [json.loads(line) for line in SAMPLES.read_text(encoding="utf-8").splitlines() if line.strip()]
    problems: list[str] = []
    notes: list[str] = []

    # --- 1. 上游结构校验 ---
    try:
        validate_samples(rows)
    except Exception as error:  # noqa: BLE001
        problems.append(f"上游 validate_samples 失败：{error}")

    # --- 2. 数量与比例 ---
    splits = collections.Counter(r["split"] for r in rows)
    total = len(rows)
    if total < MIN_TOTAL:
        problems.append(f"有效条数 {total} < {MIN_TOTAL}")
    for name in ("dev", "val", "sealed"):
        if splits[name] == 0:
            problems.append(f"{name} 集为空")
    if total:
        notes.append(f"总量 {total}；dev {splits['dev']} / val {splits['val']} / sealed {splits['sealed']}")

    # --- 3. 覆盖配额 ---
    issues_of = lambda r: r["expected_issues"]
    checks = {
        "完整需求(complete)": sum(1 for r in rows if r["expected_requirement"]["status"] == "complete"),
        "缺失(missing_field)": sum(1 for r in rows if any(i["type"] == "missing_field" for i in issues_of(r))),
        "非法(invalid_value)": sum(1 for r in rows if any(i["type"] == "invalid_value" for i in issues_of(r))),
        "冲突(conflicting_values)": sum(1 for r in rows if any(i["type"] == "conflicting_values" for i in issues_of(r))),
        "多问题(≥2 问题)": sum(1 for r in rows if len(issues_of(r)) >= 2),
        "禁止推断": sum(1 for r in rows if "no_inference" in r["tags"]),
        "多轮检查点": sum(1 for r in rows if r.get("conversation_id")),
    }
    sessions = {r["conversation_id"] for r in rows if r.get("conversation_id")}
    notes.append(f"独立会话 {len(sessions)}；语义组 {len({r['semantic_group'] for r in rows})}")

    if checks["冲突(conflicting_values)"] < MIN_CONFLICT:
        problems.append(f"冲突样本 {checks['冲突(conflicting_values)']} < {MIN_CONFLICT}")
    if checks["多问题(≥2 问题)"] < MIN_MULTI_ISSUE:
        problems.append(f"多问题组合 {checks['多问题(≥2 问题)']} < {MIN_MULTI_ISSUE}")
    if checks["多轮检查点"] < MIN_MULTI_TURN_POINTS:
        problems.append(f"多轮检查点 {checks['多轮检查点']} < {MIN_MULTI_TURN_POINTS}")
    if len(sessions) < MIN_MULTI_TURN_SESSIONS:
        problems.append(f"多轮会话数 {len(sessions)} < {MIN_MULTI_TURN_SESSIONS}")
    if checks["禁止推断"] < MIN_NO_INFERENCE:
        problems.append(f"禁止推断 {checks['禁止推断']} < {MIN_NO_INFERENCE}")

    # 冲突须覆盖书体与时长，且每个分集都有冲突
    conflict_rows = [r for r in rows if any(i["type"] == "conflicting_values" for i in issues_of(r))]
    c_fields = {i["field"] for r in conflict_rows for i in issues_of(r) if i["type"] == "conflicting_values"}
    for field in ("font", "duration_minutes"):
        if field not in c_fields:
            problems.append(f"冲突未覆盖字段 {field}")
    for name in ("dev", "val", "sealed"):
        if not any(r["split"] == name for r in conflict_rows):
            problems.append(f"{name} 集无冲突样本")

    # 完整需求须覆盖三种书体与三档时长
    complete_rows = [r for r in rows if r["expected_requirement"]["status"] == "complete"]
    fonts = {r["expected_requirement"]["font"] for r in complete_rows}
    durs = {r["expected_requirement"]["duration_minutes"] for r in complete_rows}
    if fonts != {"楷书", "行书", "行楷"}:
        problems.append(f"完整需求书体覆盖不全：{sorted(fonts)}")
    if durs != {5, 15, 30}:
        problems.append(f"完整需求时长覆盖不全：{sorted(durs)}")

    # 非法须覆盖：不支持书体、非标准正整数、负数、0、小数、单位换算后不支持
    inv_rows = [r for r in rows if any(i["type"] == "invalid_value" for i in issues_of(r))]
    inv_kinds = set()
    for r in inv_rows:
        for i in issues_of(r):
            if i["type"] != "invalid_value":
                continue
            value = i["value"]
            if i["field"] == "font":
                inv_kinds.add("unsupported_font")
            elif isinstance(value, (int, float)) and not isinstance(value, bool):
                if value < 0:
                    inv_kinds.add("negative")
                elif value == 0:
                    inv_kinds.add("zero")
                elif isinstance(value, float):
                    inv_kinds.add("decimal")
                elif value not in (5, 15, 30):
                    inv_kinds.add("nonstandard_positive")
            else:
                inv_kinds.add("unit_conversion")
    for kind in ("unsupported_font", "nonstandard_positive", "negative", "zero", "decimal", "unit_conversion"):
        if kind not in inv_kinds:
            problems.append(f"非法值未覆盖类型：{kind}")

    # --- 4. 分集隔离（语义组、会话、精确重复输入） ---
    group_split, conv_split, input_split = {}, {}, {}
    for r in rows:
        if group_split.setdefault(r["semantic_group"], r["split"]) != r["split"]:
            problems.append(f"语义组跨集：{r['semantic_group']}")
        if r.get("conversation_id"):
            if conv_split.setdefault(r["conversation_id"], r["split"]) != r["split"]:
                problems.append(f"会话跨集：{r['conversation_id']}")
        if input_split.setdefault(r["input"], r["split"]) != r["split"]:
            problems.append("相同输入跨集")

    # --- 5. 近重复（同 split 内相似度 >= 0.92 的输入） ---
    near = []
    for split in ("dev", "val", "sealed"):
        subset = [r for r in rows if r["split"] == split]
        for i in range(len(subset)):
            for j in range(i + 1, len(subset)):
                ratio = difflib.SequenceMatcher(None, subset[i]["input"], subset[j]["input"]).ratio()
                if ratio >= 0.92:
                    near.append((split, subset[i]["id"], subset[j]["id"], round(ratio, 3)))
    # 同会话的多轮检查点天然相似，不计入近重复
    near = [n for n in near if not _same_session(rows, n[1], n[2])]

    # --- 6. 无旧字段 ---
    for r in rows:
        for banned in ("goal", "exclusions", "style", "follow_up"):
            if banned in r["expected_requirement"]:
                problems.append(f"{r['id']} 含旧字段 {banned}")

    # --- 7. 清单与哈希 ---
    digest = hashlib.sha256(SAMPLES.read_bytes()).hexdigest()
    manifest = {
        "dataset": "moling-v2-eval",
        "protocol_version": "v2",
        "samples_file": "v2_eval/samples_v2.jsonl",
        "samples_sha256": digest,
        "total": total,
        "splits": {
            name: {
                "count": splits[name],
                "ids": [r["id"] for r in rows if r["split"] == name],
                "semantic_groups": sorted({r["semantic_group"] for r in rows if r["split"] == name}),
                "conversations": sorted({r["conversation_id"] for r in rows if r["split"] == name and r.get("conversation_id")}),
            }
            for name in ("dev", "val", "sealed")
        },
        "coverage": checks,
        "sessions": sorted(sessions),
        "semantic_group_count": len({r["semantic_group"] for r in rows}),
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # --- 汇总 ---
    lines = ["# v2 评测集校验报告", "",
             f"- 样本文件：`v2_eval/samples_v2.jsonl`",
             f"- SHA256：`{digest}`",
             f"- 校验时间：由脚本生成", "",
             "## 1. 结构与隔离", "",
             f"- 上游 `parsing/eval_v2.validate_samples`：{'通过' if not any('上游' in p for p in problems) else '失败'}",
             f"- 合规：{'通过' if not problems else f'发现 {len(problems)} 项问题'}", ""]
    if problems:
        lines += ["### 待解决问题", ""] + [f"- {p}" for p in problems] + [""]
    lines += ["## 2. 数量与覆盖", "", "| 维度 | 数量 |", "|---|---|"]
    for key, value in checks.items():
        lines.append(f"| {key} | {value} |")
    lines += ["", f"- 独立会话：{len(sessions)}；语义组：{manifest['semantic_group_count']}", "",
              "## 3. 分集", "", "| 分集 | 条数 | 语义组 | 会话 |", "|---|---|---|---|"]
    for name in ("dev", "val", "sealed"):
        entry = manifest["splits"][name]
        lines.append(f"| {name} | {entry['count']} | {len(entry['semantic_groups'])} | {len(entry['conversations'])} |")
    lines += ["", "## 4. 近重复检查", ""]
    if near:
        lines += ["相似度 ≥ 0.92 的输入对（已排除同会话多轮）：", ""] + [
            f"- `{s}` {a} ↔ {b}（{r}）" for s, a, b, r in near] + [""]
    else:
        lines += ["未发现相似度 ≥ 0.92 的跨样本输入（同会话多轮检查点已排除）。", ""]
    lines += ["## 5. 备注", ""] + [f"- {n}" for n in notes] + [
        "",
        "> 本报告由 `v2_eval/scripts/validate_v2.py` 自动产出。",
        "> 通过自动校验不等于真实模型全部正确，也不代表追问语义已通过人工复核。", ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    print(f"总量 {total}：dev {splits['dev']} / val {splits['val']} / sealed {splits['sealed']}")
    print(f"覆盖：{checks}")
    print(f"近重复对：{len(near)}")
    if problems:
        print(f"\n发现 {len(problems)} 项问题：")
        for p in problems:
            print(" -", p)
        return 1
    print("\n全部校验通过。")
    return 0


def _same_session(rows, id_a, id_b):
    index = {r["id"]: r for r in rows}
    a, b = index.get(id_a), index.get(id_b)
    return bool(a and b and a.get("conversation_id") and a.get("conversation_id") == b.get("conversation_id"))


def rows_of(_):
    return []


if __name__ == "__main__":
    raise SystemExit(main())
