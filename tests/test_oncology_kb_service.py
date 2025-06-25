import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from services.oncology_kb.main import router as onco_router
from shared.models import BusinessError


@pytest.mark.asyncio
async def test_oncology_query(monkeypatch):
    async def fake_search(query, cancer):
        return [{"snippet": "info", "source": "OncoKB", "url": "u"}]

    async def fake_route_llm(
        domain,
        messages,
        ctx_tokens,
        cost_sensitive=True,
    ):
        return {
            "answer": "ok",
            "citations": ["u"],
            "evidence_level": "A",
            "update_timestamp": "today",
        }

    monkeypatch.setattr(
        "services.oncology_kb.kb_tool.oncokb_search",
        fake_search,
    )
    monkeypatch.setattr(
        "services.oncology_kb.main.route_llm",
        fake_route_llm,
    )

    app = FastAPI()
    app.include_router(onco_router)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.post(
            "/v1/oncology/query",
            json={
                "cancer": "lunge",
                "query": "therapy?",
                "patient": {
                    "age": 60,
                    "gender": "M",
                    "stage": "II",
                    "biomarkers": None,
                },
            },
        )
    assert resp.status_code == 200
    assert resp.json()["answer"] == "ok"


@pytest.mark.asyncio
async def test_oncology_no_hit(monkeypatch):
    async def fake_search(query, cancer):
        raise BusinessError(404, "No KB hit")

    monkeypatch.setattr(
        "services.oncology_kb.kb_tool.oncokb_search",
        fake_search,
    )

    app = FastAPI()
    app.include_router(onco_router)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.post(
            "/v1/oncology/query",
            json={
                "cancer": "lunge",
                "query": "nothing",
                "patient": {
                    "age": 60,
                    "gender": "M",
                    "stage": "II",
                    "biomarkers": None,
                },
            },
        )
    assert resp.status_code == 404
