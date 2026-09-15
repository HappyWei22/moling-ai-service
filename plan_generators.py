"""可替换的计划生成器：接收结构化需求，返回待校验的计划字典。"""

from typing import Any
from uuid import uuid4

from schemas import GRID_BUDGETS, UserRequirement


def mock_generate(requirement: UserRequirement) -> dict[str, Any]:
    """固定候选仅用于联调；调用前由服务层检查需求是否就绪。"""
    words = ["课堂", "学习"]
    repeat = GRID_BUDGETS[requirement.duration_minutes] // sum(map(len, words))
    return {
        "schema_version": "0.3",
        "plan_id": str(uuid4()),
        "plan_name": "临摹字帖联调样例",
        "style": requirement.style,
        "duration_minutes": requirement.duration_minutes,
        "is_mock": True,
        "items": [
            {
                "text": word,
                "repeat": repeat,
                "task_type": "临摹",
                "instruction": "观察范字，注意字的大小和间距。",
            }
            for word in words
        ],
    }
