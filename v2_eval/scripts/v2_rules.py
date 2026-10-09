"""按 v2 口径生成评测样本。

设计要点：
1. 判据完全对齐 parsing/parse_requirement_v2.py 的 _collect_errors / _finalize_v2，
   生成后立即用上游 finalize_v2 回灌，逐条断言标准答案与真实本地行为一致。
2. 语义组是分集的原子单位，组内所有条目（含多轮检查点、同义改写）进同一 split。
3. 不产出旧字段（goal / exclusions / style / follow_up）。
"""

from __future__ import annotations

# ---------------------------------------------------------------- 基础枚举

FONTS = ("楷书", "行书", "行楷")
DURATIONS = (5, 15, 30)

# 书体别名（prompt_v2.md 与 parse_requirement_v2.FONT_ALIASES 一致）
FONT_ALIAS = {"楷体": "楷书", "行楷体": "行楷"}
# 职业别名
OCC_ALIAS = {"老师": "教师", "小学生": "学生"}


def mk_error(kind: str, field: str, value=None) -> dict:
    return {"type": kind, "field": field, "value": value}


# ---------------------------------------------------------------- 期望推导

def expected_status(issues: list[dict]) -> str:
    types = {i["type"] for i in issues}
    if "invalid_value" in types:
        return "invalid"
    if "conflicting_values" in types:
        return "conflict"
    if issues:
        return "needs_clarification"
    return "complete"


def model_errors_of(issues: list[dict]) -> list[dict]:
    """模型只报非法值与冲突；缺失由本地补。"""
    return [i for i in issues if i["type"] != "missing_field"]


def derive(
    *, occupation=None, scene=None, font=None, duration=None, issues=None,
    font_raw=None, duration_raw=None,
):
    """从「模型原始候选」推导标准答案。

    occupation/scene/font/duration 传入的是**归一化后**的值；
    font_raw/duration_raw 是模型原值，用于和 issues 里的 value 对齐。

    实现细节：_collect_errors 会对 font/duration 做一次本地校验——
    只要候选原值非空且不在支持集合内，就**额外**补一条 invalid_value，
    与模型已报的 conflicting_values 并存。因此冲突样本的问题集合里
    冲突字段通常**同时**带 conflicting_values 和 invalid_value，
    状态随之升到 invalid（invalid 优先级高于 conflict）。
    """
    issues = list(issues or [])

    # 1) 原值不在支持集合内 → 本地补非法值（与冲突并存）
    #
    # 上游已知缺陷 E8：纯冲突输入（如两个合法书体并列）会被**额外**补一条
    # invalid_value，导致状态由 conflict 降级为 invalid，conflict 实际不可达。
    # 本数据集按「真实代码行为」标注，并把该缺陷登记在 争议裁决表.md。
    # 若上游修掉 E8（冲突字段不再补 invalid_value），这里的结果会与其不一致，
    # 需同步重新标注并登记版本变更。
    raw_values = {"font": font_raw if font_raw is not None else font,
                  "duration_minutes": duration_raw if duration_raw is not None else duration}
    for field, supported in (("font", FONTS), ("duration_minutes", DURATIONS)):
        raw = raw_values[field]
        if raw is None:
            continue
        value = font if field == "font" else duration
        if value is None or value not in supported:
            if not any(i["type"] == "invalid_value" and i["field"] == field for i in issues):
                issues.append(mk_error("invalid_value", field, raw))

    bad_fields = {i["field"] for i in issues if i["type"] != "missing_field"}

    # 2) 非法/冲突字段置空
    if "font" in bad_fields:
        font = None
    if "duration_minutes" in bad_fields:
        duration = None

    # 3) 本地补缺失
    for field in ("font", "duration_minutes"):
        if (font if field == "font" else duration) is None and field not in bad_fields:
            if not any(i["type"] == "missing_field" and i["field"] == field for i in issues):
                issues.append(mk_error("missing_field", field))
    if occupation is None and scene is None and not bad_fields & {"occupation", "scene"}:
        if not any(i["field"] in ("occupation", "scene", "personalization") for i in issues):
            issues.append(mk_error("missing_field", "personalization"))

    status = expected_status(issues)
    req = {
        "occupation": occupation,
        "scene": scene,
        "font": font,
        "duration_minutes": duration,
        "status": status,
    }
    return req, issues


def sort_issues(issues: list[dict]) -> list[dict]:
    """与 _collect_errors 末尾的排序保持一致，便于肉眼核对。"""
    order = {"font": 0, "duration_minutes": 1, "occupation": 2, "scene": 3, "personalization": 4}
    return sorted(issues, key=lambda i: order.get(i["field"], 5))
