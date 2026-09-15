from schemas import UserRequirement

class RequirementNotReadyError(ValueError):
    """需求尚未满足生成条件。"""
    pass


def has_text(value: str | None) -> bool:
    return value is not None and value.strip() != ""

def check_requirement_ready(requirement: UserRequirement) -> None:
    if requirement.status != "complete":
        raise RequirementNotReadyError(
            f"需求尚不能用于生成计划，当前状态：{requirement.status}"
        )

    if requirement.errors:
        raise RequirementNotReadyError("需求中仍有错误记录，不能生成计划")

    if requirement.style is None:
        raise RequirementNotReadyError("缺少书体，不能生成计划")

    if requirement.duration_minutes is None:
        raise RequirementNotReadyError("缺少练习时长，不能生成计划")

    has_personalization = (
        has_text(requirement.occupation)
        or has_text(requirement.scene)
        or has_text(requirement.goal)
    )

    if not has_personalization:
        raise RequirementNotReadyError("职业、使用场景、练习目标至少需要明确一项")

    if requirement.duration_minutes not in (5, 15, 30):
        raise RequirementNotReadyError("当前仅支持 5、15、30 分钟，不自动修改用户时长")

    if requirement.exclusions:
        raise RequirementNotReadyError("当前模拟生成器尚不能可靠处理排除要求，请等待内容筛选接入")
