from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ai_service import generate_plan
from requirement_rules import RequirementNotReadyError
from schemas import UserRequirement, WorksheetPlan


app = FastAPI(title="墨灵 AI 调试服务")


class ErrorField(BaseModel):
    field: str
    message: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    fields: list[ErrorField]


class ErrorResponse(BaseModel):
    detail: ErrorDetail


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(request, error: RequestValidationError):
    fields = []
    for item in error.errors():
        location = item.get("loc", ())
        if location and location[0] == "body":
            location = location[1:]
        fields.append(ErrorField(
            field=".".join(str(part) for part in location) or "body",
            message=item["msg"],
        ))
    response = ErrorResponse(detail=ErrorDetail(
        code="VALIDATION_ERROR",
        message="请求字段不符合要求",
        fields=fields,
    ))
    return JSONResponse(status_code=422, content=response.model_dump())


@app.post("/plan", response_model=WorksheetPlan,
          responses={422: {"model": ErrorResponse, "description": "请求字段错误或需求未就绪"}})
def create_plan(requirement: UserRequirement):
    try:
        return generate_plan(requirement)
    except RequirementNotReadyError as error:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "REQUIREMENT_NOT_READY",
                "message": str(error),
                "fields": [],
            },
        ) from error
