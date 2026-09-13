from fastapi import FastAPI, HTTPException

from ai_service import generate_plan
from requirement_rules import RequirementNotReadyError
from schemas import UserRequirement, WorksheetPlan


app = FastAPI(title="墨灵 AI 调试服务")


@app.post("/plan", response_model=WorksheetPlan)
def create_plan(requirement: UserRequirement):
    try:
        return generate_plan(requirement)
    except RequirementNotReadyError as error:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "REQUIREMENT_NOT_READY",
                "message": str(error),
            },
        ) from error