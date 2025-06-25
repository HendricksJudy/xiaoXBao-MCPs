import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from services.psychology.main import router as psych_router


@pytest.mark.asyncio
async def test_psychology_chat(monkeypatch):
    async def fake_classifier(phq9, gad7):
        return "low"

    async def fake_route_llm(
        domain,
        messages,
        ctx_tokens,
        cost_sensitive=False,
    ):
        return {"result": "ok"}

    monkeypatch.setattr(
        "services.psychology.risk_tool.phq_gad_classifier",
        fake_classifier,
    )
    monkeypatch.setattr(
        "services.psychology.main.route_llm",
        fake_route_llm,
    )

    app = FastAPI()
    app.include_router(psych_router)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.post(
            "/v1/psychology/chat",
            json={"messages": [{"role": "user", "content": "hi"}]},
        )
    assert resp.status_code == 200
    assert resp.json() == {"result": "ok"}


@pytest.mark.asyncio
async def test_psychology_bad_schema(monkeypatch):
    async def fake_classifier(phq9, gad7):
        return "low"

    async def fake_route_llm(
        domain,
        messages,
        ctx_tokens,
        cost_sensitive=False,
    ):
        return {"unexpected": True}

    monkeypatch.setattr(
        "services.psychology.risk_tool.phq_gad_classifier",
        fake_classifier,
    )
    monkeypatch.setattr(
        "services.psychology.main.route_llm",
        fake_route_llm,
    )

    app = FastAPI()
    app.include_router(psych_router)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.post(
            "/v1/psychology/chat",
            json={"messages": [{"role": "user", "content": "hi"}]},
        )
    assert resp.status_code == 500
