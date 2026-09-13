import json
from pathlib import Path

from pydantic import ValidationError

from schemas import UserRequirement
from ai_service import generate_plan
from requirement_rules import RequirementNotReadyError


examples_path = (
    Path(__file__).parent
    / "user_requirement"
    / "examples_v0.3.json"
)

examples = json.loads(
    examples_path.read_text(encoding="utf-8")
)

# 根据已经审核过的样例，明确哪些应该允许生成
allowed_ids = {"UR-01", "UR-02", "UR-03", "UR-07"}

passed = 0

for example in examples:
    example_id = example["id"]
    should_allow = example_id in allowed_ids

    # 第一关：参考答案能否创建为需求对象
    try:
        requirement = UserRequirement.model_validate(
            example["expected"]
        )
    except ValidationError as error:
        print(f"{example_id} 失败：需求结构不符合协议")
        print(error)
        continue

    # 第二关：生成入口是否正确放行或拦截
    try:
        generate_plan(requirement)
    except RequirementNotReadyError as error:
        actual_allow = False
        message = str(error)
    else:
        actual_allow = True
        message = "返回模拟计划"

    if actual_allow == should_allow:
        passed += 1
        print(f"{example_id} 通过：{message}")
    else:
        print(f"{example_id} 失败：放行或拦截结果与预期不一致")

print(f"\n验证结果：{passed}/{len(examples)} 通过")