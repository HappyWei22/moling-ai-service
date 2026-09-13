from schemas import UserRequirement, WorksheetItem, WorksheetPlan


def generate_plan(requirement: UserRequirement) -> WorksheetPlan:
    plan = WorksheetPlan(
        duration_minutes=requirement.duration_minutes,
        is_mock=True,
        items=[
            WorksheetItem(text="教师", repeat=3)
        ],
    )

    return plan