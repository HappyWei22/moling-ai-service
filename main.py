from fastapi import FastAPI

from ai_service import generate_plan
from schemas import UserRequirement, WorksheetPlan


app = FastAPI(title="墨灵 AI 调试服务")


@app.post("/plan", response_model=WorksheetPlan)
def create_plan(requirement: UserRequirement):
    return generate_plan(requirement)