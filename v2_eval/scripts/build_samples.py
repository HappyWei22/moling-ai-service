"""把 sample_specs 编译为 v2_eval/samples_v2.jsonl，并用上游真实实现回灌校验。

关键纪律：标准答案不是手写死的，而是由 spec 推导后**再用 finalize_v2 实跑一遍**，
逐条比对 五字段答案 / 问题集合 / 状态。任何不一致都会中止构建并打印差异。
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from parsing.parse_requirement_v2 import FONT_ALIASES  # noqa: E402
from parsing.parse_requirement_v2 import _finalize_v2  # noqa: E402
import sample_specs  # noqa: E402
from v2_rules import derive, model_errors_of, sort_issues  # noqa: E402

OUT = ROOT / "v2_eval" / "samples_v2.jsonl"
SPLIT_DIR = ROOT / "v2_eval" / "splits"

# 分集覆盖：把以下语义组从各自声明的位置整体挪到 val，
# 使最终比例贴近 60/20/20（多轮检查点天然堆在 dev，需人工再平衡）。
# 这些组均为单条新建组、未用于调试，挪动不违反「sealed 不使用已调试内容」的纪律。
TO_VAL = {
    "V2-G015",
}


def raw_of(spec: dict, field: str):
    """模型在该字段上的候选原值：优先取非法/冲突记录里的 value，否则取字面声明。"""
    for i in spec.get("issues", []):
        if i["field"] == field and i["type"] in ("invalid_value", "conflicting_values"):
            return i["value"]
    if field == "font":
        return spec.get("font_in", spec.get("font"))
    return spec.get("dur")


def build_candidate(spec: dict) -> dict:
    """还原「模型原始六字段输出」。font/duration 用原值，便于和 issues.value 对齐。"""
    return {
        "occupation": spec.get("occ"),
        "scene": spec.get("scene"),
        "font": raw_of(spec, "font"),
        "duration_minutes": raw_of(spec, "duration_minutes"),
        "status": "needs_clarification",
        "errors": [i for i in spec.get("issues", []) if i["type"] != "missing_field"],
    }


def cross_check(spec: dict, expected: dict, issues: list[dict]) -> list[str]:
    """用上游真实实现回灌，返回差异列表（空 = 一致）。"""
    candidate = build_candidate(spec)
    req, _msg, real_issues = _finalize_v2(candidate)
    problems = []
    real = req.model_dump()
    for field in ("occupation", "scene", "font", "duration_minutes", "status"):
        if real[field] != expected[field]:
            problems.append(f"字段 {field}: 期望 {expected[field]!r} 实得 {real[field]!r}")
    key = lambda xs: sorted((i["type"], i["field"]) for i in xs)
    if key(real_issues) != key(issues):
        problems.append(f"问题集合: 期望 {key(issues)} 实得 {key(real_issues)}")
    return problems


def main() -> int:
    rows, failures = [], []
    seen_ids, seen_inputs = set(), {}
    group_split = {}

    for index, spec in enumerate(sample_specs.ALL, 1):
        group = spec["g"]
        split = "val" if group in TO_VAL else spec["sp"]
        # 语义组隔离：同一组不得跨集
        if group_split.setdefault(group, split) != split:
            failures.append(f"{group}: 语义组跨分集")
        if spec.get("cid"):
            if group_split.setdefault(f"conv:{spec['cid']}", split) != split:
                failures.append(f"{spec['cid']}: 会话跨分集")

        expected, issues = derive(
            occupation=spec.get("occ"), scene=spec.get("scene"),
            font=spec.get("font"), duration=spec.get("dur"),
            issues=spec.get("issues", []),
            font_raw=raw_of(spec, "font"),
            duration_raw=raw_of(spec, "duration_minutes"),
        )
        issues = sort_issues(issues)
        problems = cross_check(spec, expected, issues)
        if problems:
            failures.append(f"[{group} turn={spec.get('turn')}] " + "; ".join(problems))

        # id：多轮检查点用 turn 后缀
        sid = f"V2-{'D' if split == 'dev' else 'V' if split == 'val' else 'S'}{index:03d}"
        if sid in seen_ids:
            failures.append(f"id 重复 {sid}")
        seen_ids.add(sid)

        text = spec["input"]
        if text in seen_inputs and seen_inputs[text] != split:
            failures.append(f"{sid}: 相同输入跨分集")
        seen_inputs[text] = split

        complete = expected["status"] == "complete"
        row = {
            "id": sid,
            "protocol_version": "v2",
            "split": split,
            "semantic_group": group,
            "tags": sorted(set(spec.get("tags", []))),
            "input": text,
            "conversation_id": spec.get("cid"),
            "turn_index": spec.get("turn"),
            "user_turns": spec.get("turns") or [text],
            "source": {"kind": spec.get("kind", "new"), "v1_id": spec.get("v1")},
            "expected_requirement": expected,
            "expected_model_errors": model_errors_of(issues),
            "expected_issues": issues,
            "expected_api": {
                "http_status": 200,
                "code": 0 if complete else 400,
                "data": expected if complete else None,
                **({"message": "ok"} if complete else {}),
            },
            "message_check": {
                "required": required_topics(issues),
                "forbidden": forbidden_topics(issues),
            },
            "rationale": spec.get("rationale", "").strip(),
            "evidence": evidence_of(issues),
            "annotator": "罗占勇",
            "reviewer": "待复核",
        }
        rows.append(row)

    if failures:
        print("构建中止，发现以下不一致：")
        for item in failures:
            print(" -", item)
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    # 分集物理分开保存，便于隔离
    SPLIT_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("dev", "val", "sealed"):
        subset = [r for r in rows if r["split"] == name]
        path = SPLIT_DIR / f"samples_v2_{name}.jsonl"
        with path.open("w", encoding="utf-8") as handle:
            for row in subset:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    import collections
    print(f"写出 {len(rows)} 条 → {OUT.relative_to(ROOT)}")
    print("分集：", dict(collections.Counter(r["split"] for r in rows)))
    print("语义组数：", len({r["semantic_group"] for r in rows}))
    print("SHA256：", hashlib.sha256(OUT.read_bytes()).hexdigest()[:16])
    return 0


LABELS = {"font": "书体", "duration_minutes": "练习时长", "occupation": "职业",
          "scene": "书写场景", "personalization": "职业或书写场景"}


def required_topics(issues):
    out = []
    for item in issues:
        label = LABELS[item["field"]]
        if item["type"] == "missing_field":
            out.append(f"询问{label}")
        elif item["type"] == "invalid_value":
            out.append(f"指出{label}非法并要求修改或重给")
        else:
            out.append(f"指出{label}冲突并要求确认以哪个为准")
    if not out:
        out.append("直接确认需求已完整并给出结果")
    return out


def forbidden_topics(issues):
    """按固定字段顺序生成 forbidden 清单。

    注意：这里**不能**用 set 迭代（`bad = {..}`），因为 Python 字符串哈希有随机化，
    set 的遍历顺序在不同进程间不稳定，会导致 samples_v2.jsonl 的字节内容与 SHA256
    每次都变、无法复现。改用与 _collect_errors 一致的固定字段顺序。
    """
    out = []
    order = ("font", "duration_minutes", "occupation", "scene", "personalization")
    bad = [f for f in order if any(
        i["field"] == f and i["type"] != "missing_field" for i in issues)]
    for field in bad:
        out.append(f"重复询问{LB[field]}缺失")
    if issues:
        out.append("直接生成计划")
    if any(i["field"] == "personalization" for i in issues):
        out.append("分别强制补职业和场景")
    return out


LB = LABELS


def evidence_of(issues):
    return {i["field"]: i.get("value") for i in issues if i.get("value") is not None}


if __name__ == "__main__":
    raise SystemExit(main())
