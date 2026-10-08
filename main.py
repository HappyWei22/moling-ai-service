from fastapi import FastAPI, HTTPException, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ai_service import generate_plan, generate_plan_v2
from parsing.errors import ParseConfigError, ParseFormatError, ParseTransportError
from parsing.parse_requirement import parse_text
from parsing.parse_requirement_v2 import parse_text_v2
from requirement_rules import RequirementNotReadyError
from schemas import ParsedRequirementV2, UserRequirement, WorksheetPlan


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


class ParseRequest(BaseModel):
    model_config = {"extra": "forbid"}

    text: str = Field(min_length=1, title="用户原话", description="一句自然语言练字需求，例如“我是老师，每天练15分钟，想练楷书”。")


class ParseV2Response(BaseModel):
    code: int
    message: str
    data: ParsedRequirementV2 | None


PARSE_RESPONSES = {
    422: {"model": ErrorResponse, "description": "请求字段错误，或模型输出无法解析成需求协议"},
    502: {"model": ErrorResponse, "description": "模型调用失败（网络、超时或接口错误）"},
    503: {"model": ErrorResponse, "description": "服务端缺少模型配置（密钥）"},
}


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


@app.post("/parse", response_model=UserRequirement, responses=PARSE_RESPONSES)
def parse_requirement(response: Response, request: ParseRequest):
    """把自然语言解析成 UserRequirement。

    解析结果始终返回 200，业务状态看响应体的 status：
    complete / needs_clarification / conflict / invalid。
    只有格式无法解析、调用失败或缺少配置才返回错误码。
    """
    try:
        outcome = parse_text(request.text)
    except ParseConfigError as error:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "PARSE_CONFIG_ERROR",
                "message": str(error) + (f"；{error.hint}" if error.hint else ""),
                "fields": [],
            },
        ) from error
    except ParseTransportError as error:
        raise HTTPException(
            status_code=502,
            detail={
                "code": "PARSE_TRANSPORT_ERROR",
                "message": str(error)[:300],
                "fields": [],
            },
        ) from error
    except ParseFormatError as error:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "PARSE_FORMAT_ERROR",
                "message": str(error)[:300],
                "fields": [
                    ErrorField(field=name, message="模型输出缺少该字段")
                    for name in error.missing_keys
                ],
            },
        ) from error

    response.headers["X-Moling-Client"] = outcome.client
    response.headers["X-Moling-Model"] = outcome.model
    response.headers["X-Moling-Prompt-Version"] = outcome.prompt_version
    return outcome.requirement


@app.post("/parse/v2", response_model=ParseV2Response, responses=PARSE_RESPONSES)
def parse_requirement_v2(response: Response, request: ParseRequest):
    """无状态解析；后端须传入已合并的完整会话文本。"""
    try:
        outcome = parse_text_v2(request.text)
    except ParseConfigError as error:
        raise HTTPException(status_code=503, detail={
            "code": "PARSE_CONFIG_ERROR", "message": str(error), "fields": [],
        }) from error
    except ParseTransportError as error:
        raise HTTPException(status_code=502, detail={
            "code": "PARSE_TRANSPORT_ERROR", "message": str(error)[:300], "fields": [],
        }) from error
    except ParseFormatError as error:
        raise HTTPException(status_code=422, detail={
            "code": "PARSE_FORMAT_ERROR", "message": str(error)[:300], "fields": [],
        }) from error

    response.headers["X-Moling-Client"] = outcome.client
    response.headers["X-Moling-Model"] = outcome.model
    response.headers["X-Moling-Prompt-Version"] = "v2"
    complete = outcome.requirement.status == "complete"
    return ParseV2Response(
        code=0 if complete else 400,
        message=outcome.message,
        data=outcome.requirement if complete else None,
    )


@app.post("/plan/v2", response_model=WorksheetPlan,
          responses={422: {"model": ErrorResponse, "description": "需求未就绪"}})
def create_plan_v2(requirement: ParsedRequirementV2):
    try:
        return generate_plan_v2(requirement)
    except RequirementNotReadyError as error:
        raise HTTPException(status_code=422, detail={
            "code": "REQUIREMENT_NOT_READY", "message": str(error), "fields": [],
        }) from error
