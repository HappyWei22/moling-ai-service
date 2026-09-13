from schemas import UserRequirement
from ai_service import generate_plan


try:
    requirement = UserRequirement(
        occupation="教师",
        scene=None,
        style="楷书",
        duration_minutes=15,
        goal=None,
        exclusions=[],
        status="complete",
        follow_up=None,
        errors=[],
    )


    result = generate_plan(requirement)

except ValueError as error:
    print("不能生成：", error)

else:
    print("计划生成成功：")
    print(result.model_dump_json(indent=2))