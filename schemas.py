from pydantic import BaseModel, Field

class UserRequirement(BaseModel):
    duration_minutes: int = Field(gt=0)

class WorksheetItem(BaseModel):
    text: str = Field(min_length=1)
    repeat: int = Field(gt=0)

class WorksheetPlan(BaseModel):
    duration_minutes: int = Field(gt=0)
    is_mock: bool
    items: list[WorksheetItem] = Field(min_length=1)