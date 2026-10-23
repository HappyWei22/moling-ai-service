"""多批次评测结果横向对比，输出 markdown。

用途：同一套评测集、同一份提示词、不同模型/硬件的批次，放在一张表里比。
      `eval_v2.py` 每批只出「自己 vs 期望」，跨批次对比要手工拼，容易算错口径。
      这里统一口径，避免「问题集合一致」和「自动全一致」被混着引用。

用法（项目根目录）：
    python scripts_local/compare_runs.py \
        --run cloud=v2_eval/baseline/dev_val_runs.jsonl \
        --run 7b=v2_eval/baseline/local_qwen25_7b_runs.jsonl \
        --run 14b=v2_eval/baseline/local_qwen25_14b_runs.jsonl

    加 --only-common 只统计各批次都有的 sample_id（公平对比）
    加 --details 打印错误放行/漏判明细
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

FIELDS = ["occupation", "scene", "font", "duration_minutes", "status"]


def load(path: str) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rows[row["sample_id"]] = row
    return rows


def _norm_scene(value: str | None) -> str | None:
    """去掉「写/做/进行」前缀，仅供诊断口径，不替代严格比对。"""
    if not value:
        return value
    return re.sub(r"^(写|做|进行)", "", value)


def metrics(rows: dict[str, dict]) -> dict:
    values = list(rows.values())
    n = len(values)
    auto = sum(1 for r in values if r.get("automated_match"))
    issues = sum(1 for r in values if r.get("issues_match"))
    wrong = sum(1 for r in values if r.get("wrong_release"))
    hits = sum(r.get("model_error_hits") or 0 for r in values)
    expected = sum(r.get("model_error_expected") or 0 for r in values)
    actual = sum(r.get("model_error_actual") or 0 for r in values)
    lat = [r.get("latency_ms") or 0 for r in values]

    out = {
        "n": n,
        "auto": auto,
        "auto_pct": auto / n * 100 if n else 0.0,
        "issues": issues,
        "issues_pct": issues / n * 100 if n else 0.0,
        "wrong": wrong,
        # 与 eval_v2.summarize 同口径：分母是「期望状态不是 complete」的样本数，
        # 不是「模型至少报了一个错误」的样本数（后者会小很多，容易把放行率说得偏高）
        "wrong_denom": sum(1 for r in values if r["expected"].get("status") != "complete"),
        "recall": f"{hits}/{expected}",
        "recall_pct": hits / expected * 100 if expected else 0.0,
        "precision": f"{hits}/{actual}",
        "precision_pct": hits / actual * 100 if actual else 0.0,
        "latency_mean": sum(lat) / n if n else 0,
        "latency_p50": sorted(lat)[n // 2] if n else 0,
    }
    for field in FIELDS:
        out[f"f_{field}"] = sum(1 for r in values if r["expected"].get(field) == r["actual"].get(field))
        out[f"f_{field}_pct"] = out[f"f_{field}"] / n * 100 if n else 0.0
    out["scene_missing"] = sum(
        1 for r in values if r["expected"].get("scene") and not r["actual"].get("scene")
    )
    out["scene_halluc"] = sum(
        1 for r in values if not r["expected"].get("scene") and r["actual"].get("scene")
    )
    out["scene_wrong"] = sum(
        1 for r in values
        if r["expected"].get("scene") and r["actual"].get("scene")
        and r["expected"]["scene"] != r["actual"]["scene"]
    )
    out["scene_norm"] = sum(
        1 for r in values
        if r["expected"].get("scene")
        and _norm_scene(r["expected"]["scene"]) == _norm_scene(r["actual"].get("scene"))
    )
    out["scene_expected"] = sum(1 for r in values if r["expected"].get("scene"))
    return out


def _fmt(x: float, digits: int = 1) -> str:
    return f"{x:.{digits}f}"


def render(data: dict[str, dict[str, dict]], details: bool) -> str:
    labels = list(data.keys())
    lines: list[str] = []

    lines.append("| 指标 | " + " | ".join(labels) + " |")
    lines.append("|---" * (len(labels) + 1) + "|")

    # 预先算好，避免每个 row 重复计算
    ms = {k: metrics(data[k]) for k in labels}

    def line(label: str, fn):
        lines.append("| " + label + " | " + " | ".join(fn(ms[k]) for k in labels) + " |")

    line("样本数", lambda m: str(m["n"]))
    line("**自动全一致**", lambda m: f"{m['auto']}/{m['n']} ({_fmt(m['auto_pct'])}%)")
    line("完整问题集合一致", lambda m: f"{m['issues']}/{m['n']} ({_fmt(m['issues_pct'])}%)")
    line("**错误放行**", lambda m: f"{m['wrong']}/{m['wrong_denom']}")
    line("错误召回", lambda m: f"{m['recall']} ({_fmt(m['recall_pct'])}%)")
    line("错误精确", lambda m: f"{m['precision']} ({_fmt(m['precision_pct'])}%)")
    line("平均延迟", lambda m: f"{m['latency_mean']:.0f} ms")
    line("P50 延迟", lambda m: f"{m['latency_p50']:.0f} ms")
    lines.append("")
    lines.append("**字段级准确率**")
    lines.append("")
    lines.append("| 字段 | " + " | ".join(labels) + " |")
    lines.append("|---" * (len(labels) + 1) + "|")
    for field in FIELDS:
        line(field, lambda m, f=field: f"{m['f_' + f]}/{m['n']} ({_fmt(m['f_' + f + '_pct'])}%)")
    line("scene 应填未填", lambda m: str(m["scene_missing"]))
    line("scene 幻觉", lambda m: str(m["scene_halluc"]))
    line("scene 值不同", lambda m: str(m["scene_wrong"]))
    line("scene 去前缀后命中", lambda m: f"{m['scene_norm']}/{m['scene_expected']}")

    if details:
        for key in labels:
            rows = data[key]
            bad_release = [sid for sid, r in rows.items() if r.get("wrong_release")]
            if bad_release:
                lines.append("")
                lines.append(f"**{key} 错误放行（{len(bad_release)} 条）**")
                lines.append("")
                for sid in bad_release:
                    r = rows[sid]
                    lines.append(
                        f"- `{sid}` 期望 `{r['expected'].get('status')}` / 实际 `{r['actual'].get('status')}`"
                        f" — {r.get('input', '')[:60]}"
                    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="append", required=True,
                        help="label=path，可重复，如 cloud=v2_eval/baseline/dev_val_runs.jsonl")
    parser.add_argument("--only-common", action="store_true",
                        help="只统计各批次共有的 sample_id")
    parser.add_argument("--details", action="store_true")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    data: dict[str, dict[str, dict]] = {}
    for item in args.run:
        if "=" not in item:
            raise SystemExit(f"--run 需要 label=path 形式：{item}")
        label, path = item.split("=", 1)
        data[label] = load(path)

    if args.only_common:
        common = set.intersection(*(set(v) for v in data.values()))
        data = {k: {sid: r for sid, r in v.items() if sid in common} for k, v in data.items()}

    table = render(data, args.details)
    print(table)
    if args.out:
        Path(args.out).write_text(table + "\n", encoding="utf-8")
        print(f"\n已写入 {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
