import pytest
import tiktoken
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from shared.utils.safety_middleware import add_safety_middleware


@pytest.mark.asyncio
async def test_redact_request_and_response(monkeypatch):
    app = FastAPI()
    add_safety_middleware(app)

    @app.post("/echo")
    async def echo(body: dict):
        return body

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.post(
            "/echo",
            json={"msg": "contact me at test@example.com or +123456789"},
        )
    data = resp.json()
    assert data["msg"] == "contact me at [REDACTED] or [REDACTED]"


@pytest.mark.asyncio
async def test_token_cap(monkeypatch):
    app = FastAPI()
    add_safety_middleware(app)

    long_text = "a" * 2000

    @app.get("/long")
    async def long():
        return {"text": long_text}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.get("/long")
    tokens = len(tiktoken.get_encoding("cl100k_base").encode(resp.text))
    assert tokens <= 515
    assert resp.text.endswith("...")
