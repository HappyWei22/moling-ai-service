from schemas import UserRequirement
from requirement_rules import check_requirement_ready

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

try:
    check_requirement_ready(requirement)
except ValueError as error:
    print("不能生成：", error)
else:
    print("状态检查通过")