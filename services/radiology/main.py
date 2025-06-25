from fastapi import APIRouter
from pydantic import BaseModel

from shared.models import BusinessError, RadiologyResponse
from shared.utils.llm_router import route_llm

from . import constants, nlp_tool

router = APIRouter(prefix="/v1/radiology")


class ReportInput(BaseModel):
    report_text: str


@router.post("/analyze")
async def analyze(payload: ReportInput):
    await nlp_tool.extract_entities(payload.report_text)
    messages = [
        {"role": "system", "content": constants.system_prompt},
        {"role": "user", "content": payload.report_text},
    ]
    ctx_tokens = sum(len(m.get("content", "")) for m in messages)
    llm_resp = await route_llm(
        domain="radiology", messages=messages, ctx_tokens=ctx_tokens
    )
    try:
        data = RadiologyResponse.model_validate(llm_resp)
    except Exception as exc:
        raise BusinessError(500, "schema validation failed") from exc
    return data.model_dump()
