from uuid import uuid4

from schemas import UserRequirement, WorksheetItem, WorksheetPlan, GRID_BUDGETS
from requirement_rules import check_requirement_ready


def generate_plan(requirement: UserRequirement) -> WorksheetPlan:
    check_requirement_ready(requirement)
    # 固定候选仅用于接口联调，不声称满足个性化内容需求。
    words = ["课堂", "学习"]
    repeat = GRID_BUDGETS[requirement.duration_minutes] // sum(map(len, words))
    return WorksheetPlan(
        schema_version="0.3",
        plan_id=str(uuid4()),
        plan_name="临摹字帖联调样例",
        style=requirement.style,
        duration_minutes=requirement.duration_minutes,
        is_mock=True,
        items=[
            WorksheetItem(
                text=word, repeat=repeat, task_type="临摹",
                instruction="观察范字，注意字的大小和间距。",
            )
            for word in words
        ],
    )
