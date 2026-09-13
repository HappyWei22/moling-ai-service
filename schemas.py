from pydantic import BaseModel, Field
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

class WorksheetItem(BaseModel):
    text: str = Field(min_length=1)
    repeat: int = Field(gt=0)

class WorksheetPlan(BaseModel):
    duration_minutes: int = Field(gt=0)
    is_mock: bool
    items: list[WorksheetItem] = Field(min_length=1)