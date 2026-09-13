from pydantic import ValidationError

from schemas import UserRequirement
from ai_service import generate_plan


try:
    user_data = UserRequirement(duration_minutes=15)
    result = generate_plan(user_data)
except ValidationError as error:
    print("数据校验失败：")
    print(error)
else:
    print("计划生成成功：")
    print(result)

    plan_dict = result.model_dump()
    print(plan_dict)

    plan_json = result.model_dump_json(indent=2)
    print(plan_json)
    print(type(plan_json))