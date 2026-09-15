from pydantic import BaseModel, Field, model_validator
from typing import Any, Literal

class RequirementError(BaseModel):
    model_config = {"extra": "forbid"}

    type: str
    field: str
    value: Any = None

class UserRequirement(BaseModel):
    model_config = {"extra": "forbid"}

    occupation: str | None
    scene: str | None
    style: Literal["楷书", "行书", "行楷"] | None
    duration_minutes: int | None = Field(ge=1, strict=True)
    goal: str | None

    exclusions: list[str]

    status: Literal[
        "complete",
        "needs_clarification",
        "conflict",
        "invalid",
    ]

    follow_up: str | None
    errors: list[RequirementError]

# 暂定工程规则：每分钟 2.4 个填写字格，尚未经过实际练习校准。
GRID_BUDGETS = {5: 12, 15: 36, 30: 72}

class WorksheetItem(BaseModel):
    """一项临摹练习：一个连续汉字词组及整组重复次数，不包含评分。"""

    model_config = {"extra": "forbid"}

    text: str = Field(
        min_length=1, pattern=r"^[\u3400-\u4dbf\u4e00-\u9fff]+$",
        title="练习字词",
        description="一个字或词，仅接受基本区与扩展 A 区汉字，不含空格或标点；词语边界由内容提供者保证。",
    )
    repeat: int = Field(
        gt=0, strict=True, title="整组重复次数",
        description="整个 text 重复的次数；课堂重复 3 次占 6 个填写字格，不含范字。",
    )
    task_type: Literal["临摹"] = Field(
        title="练习形式", description="第一版仅支持看范字临摹，不支持描红、默写或纠错。",
    )
    instruction: str | None = Field(
        default=None, title="练习指导语", description="可省略或为 null，只作练习建议，不是评分或过关判定。",
    )


class WorksheetPlan(BaseModel):
    """墨灵 v0.3 临摹练习计划结构，不含 AI 评测或评分。"""

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$comment": (
                "本文件由 schemas.py 经 export_schemas.py 自动生成，请勿直接编辑。"
                "总填写字格数须符合 5/15/30 分钟对应 12/36/72 格的暂定规则，"
                "该跨字段计算由 Python model_validator 校验，未完整表达在 JSON Schema 中。"
                "配额未经教学验证；输入输出书体、时长的一致性由调用流程保证。"
            ),
        },
    }

    schema_version: Literal["0.3"] = Field(
        title="业务协议版本", description="墨灵计划格式版本，与 $schema 指定的 JSON Schema 标准版本不同。",
    )
    plan_id: str = Field(
        min_length=1, title="计划编号",
        description="当前模块每次调用生成新的 UUID 字符串；字段仅校验非空，不承诺请求幂等。",
    )
    plan_name: str = Field(min_length=1, title="计划名称", description="面向用户的显示名称。")
    style: Literal["楷书", "行书", "行楷"] = Field(
        title="书体", description="应与需求书体一致；具体字体文件、授权及字形覆盖由渲染端确认。",
    )
    duration_minutes: Literal[5, 15, 30] = Field(
        title="目标练习时长", description="单位分钟，应与输入一致；仅支持 5、15、30，不自动映射其他时长。",
    )
    is_mock: bool = Field(
        title="是否为模拟数据", description="当前固定候选生成器必须返回 true，不表示已完成个性化选词。",
    )
    items: list[WorksheetItem] = Field(
        min_length=1, title="练习清单", description="按列表顺序展示范字及空白练习格，至少包含一项。",
    )

    @model_validator(mode="after")
    def check_grid_budget(self):
        total = sum(len(item.text) * item.repeat for item in self.items)
        if total != GRID_BUDGETS[self.duration_minutes]:
            raise ValueError("总填写字格数不符合 v0.3 暂定训练量规则")
        return self
