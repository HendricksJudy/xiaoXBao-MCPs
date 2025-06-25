from fastapi import APIRouter
from pydantic import BaseModel

from shared.models import BusinessError, PsychologyResponse
from shared.utils.llm_router import route_llm

from . import constants, risk_tool

router = APIRouter(prefix="/v1/psychology")


class ChatInput(BaseModel):
    messages: list[dict]
    phq9: int | None = None
    gad7: int | None = None


@router.post("/chat")
async def chat(payload: ChatInput):
    await risk_tool.phq_gad_classifier(payload.phq9, payload.gad7)
    messages = [
        {"role": "system", "content": constants.system_prompt}
    ] + payload.messages
    ctx_tokens = sum(len(m.get("content", "")) for m in messages)
    llm_resp = await route_llm(
        domain="psychology",
        messages=messages,
        ctx_tokens=ctx_tokens,
        cost_sensitive=False,
    )
    try:
        data = PsychologyResponse.model_validate(llm_resp)
    except Exception:
        return BusinessError(500, "schema validation failed").to_response()
    return data.model_dump()
