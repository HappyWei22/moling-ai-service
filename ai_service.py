from collections.abc import Callable
from typing import Any

from plan_generators import mock_generate
from requirement_rules import check_requirement_ready
from schemas import ParsedRequirementV2, UserRequirement, WorksheetPlan


PlanGenerator = Callable[[UserRequirement], dict[str, Any]]


def generate_plan(
    requirement: UserRequirement,
    generator: PlanGenerator = mock_generate,
) -> WorksheetPlan:
    """检查需求、调用可替换生成器，并校验其输出。"""
    check_requirement_ready(requirement)
    # 保存输入约束，避免生成器改动需求对象后绕过一致性检查。
    expected_style = requirement.style
    expected_duration = requirement.duration_minutes
    raw_plan = generator(requirement.model_copy(deep=True))
    plan = WorksheetPlan.model_validate(raw_plan)
    if plan.style != expected_style or plan.duration_minutes != expected_duration:
        raise ValueError("生成计划的书体和时长必须与输入需求一致")
    return plan


def generate_plan_v2(requirement: ParsedRequirementV2) -> WorksheetPlan:
    """把新解析协议映射到当前尚使用 style 的计划协议。"""
    return generate_plan(UserRequirement(
        occupation=requirement.occupation,
        scene=requirement.scene,
        style=requirement.font,
        duration_minutes=requirement.duration_minutes,
        goal=None,
        exclusions=[],
        status=requirement.status,
        follow_up=None,
        errors=[],
    ))
