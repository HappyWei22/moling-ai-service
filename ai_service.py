from schemas import UserRequirement, WorksheetItem, WorksheetPlan
from requirement_rules import check_requirement_ready


def generate_plan(requirement: UserRequirement) -> WorksheetPlan:
    check_requirement_ready(requirement)

    plan = WorksheetPlan(
        duration_minutes=requirement.duration_minutes,
        is_mock=True,
        items=[
            WorksheetItem(text="教师", repeat=3)
        ],
    )

    return plan