import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from services.vision.main import router as vis_router


@pytest.mark.asyncio
async def test_vision_classify(monkeypatch):
    async def fake_load(image_id):
        return b"img"

    def fake_classify(img, top_k):
        return ([{"name": "cat", "confidence": 0.9}], False)

    monkeypatch.setattr(
        "services.vision.image_loader.load",
        fake_load,
    )
    monkeypatch.setattr(
        "services.vision.vision_tool.classify",
        fake_classify,
    )

    app = FastAPI()
    app.include_router(vis_router)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.post("/v1/vision/classify", json={"image_id": "1"})
    assert resp.status_code == 200
    data = resp.json()
    assert "labels" in data and isinstance(data["labels"], list)
