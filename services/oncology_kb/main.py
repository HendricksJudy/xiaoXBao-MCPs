from fastapi import APIRouter
from pydantic import BaseModel

from shared.models import BusinessError, OncologyKBResponse
from shared.utils.llm_router import route_llm

from . import constants, kb_tool

router = APIRouter(prefix="/v1/oncology")


class PatientInfo(BaseModel):
    age: int
    gender: str
    stage: str
    biomarkers: list[str] | None = None


class QueryInput(BaseModel):
    cancer: str
    query: str
    patient: PatientInfo


@router.post("/query")
async def query(payload: QueryInput):
    try:
        snippets = await kb_tool.oncokb_search(payload.query, payload.cancer)
    except BusinessError as e:
        return e.to_response()
    messages = [{"role": "system", "content": constants.system_prompt}]
    for sn in snippets:
        messages.append({"role": "system", "content": sn["snippet"]})
    messages.append({"role": "user", "content": payload.query})

    ctx_tokens = sum(len(m.get("content", "")) for m in messages)
    llm_resp = await route_llm(
        domain="oncology_kb",
        messages=messages,
        ctx_tokens=ctx_tokens,
        cost_sensitive=True,
    )
    try:
        data = OncologyKBResponse.model_validate(llm_resp)
    except Exception:
        return BusinessError(500, "schema validation failed").to_response()
    return data.model_dump()
