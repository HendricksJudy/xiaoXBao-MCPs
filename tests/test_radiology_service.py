import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from services.radiology.main import router as rad_router


@pytest.mark.asyncio
async def test_radiology_mri(monkeypatch):
    async def fake_extract(text):
        return ["brain"]

    async def fake_route(domain, messages, ctx_tokens):
        return {
            "findings": "normal",
            "impression": "ok",
            "follow_up": "none",
            "modalities_detected": ["MRI"],
            "uncertainty_flags": [],
        }

    monkeypatch.setattr(
        "services.radiology.nlp_tool.extract_entities",
        fake_extract,
    )
    monkeypatch.setattr(
        "services.radiology.main.route_llm",
        fake_route,
    )

    app = FastAPI()
    app.include_router(rad_router)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.post(
            "/v1/radiology/analyze",
            json={"report_text": "MRI of brain"},
        )
    assert resp.status_code == 200
    assert resp.json()["impression"] == "ok"


@pytest.mark.asyncio
async def test_radiology_ct(monkeypatch):
    async def fake_extract(text):
        return ["lung"]

    async def fake_route(domain, messages, ctx_tokens):
        return {
            "findings": "mass",
            "impression": "follow",
            "follow_up": "建议 6 个月后 HRCT 复查",
            "modalities_detected": ["CT"],
            "uncertainty_flags": ["uncertain"],
        }

    monkeypatch.setattr(
        "services.radiology.nlp_tool.extract_entities",
        fake_extract,
    )
    monkeypatch.setattr(
        "services.radiology.main.route_llm",
        fake_route,
    )

    app = FastAPI()
    app.include_router(rad_router)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.post(
            "/v1/radiology/analyze",
            json={"report_text": "CT of chest"},
        )
    assert resp.status_code == 200
    assert resp.json()["modalities_detected"] == ["CT"]
