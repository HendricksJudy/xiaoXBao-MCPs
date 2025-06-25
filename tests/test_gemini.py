import asyncio
import importlib

import httpx
import pytest
import respx
import tiktoken

from shared.models.errors import LLMApiError


class DummyEncoding:
    def encode(self, text: str):
        return list(text)


@pytest.fixture(autouse=True)
def _mock_tiktoken(monkeypatch):
    monkeypatch.setattr(tiktoken, "get_encoding", lambda name: DummyEncoding())
    import shared.adapters.gemini as gm
    importlib.reload(gm)
    return gm.gemini_chat


@respx.mock
@pytest.mark.asyncio
async def test_gemini_chat_success(_mock_tiktoken):
    gemini_chat = _mock_tiktoken
    route = respx.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:streamGenerateContent"
    ).mock(return_value=httpx.Response(200, json={"ok": True}))

    result = await gemini_chat([{"role": "user", "content": "hi"}])
    assert result == {"ok": True}
    assert route.called
    import json
    payload = json.loads(route.calls[0].request.content.decode())
    assert payload["response_mime_type"] == "application/json"


@respx.mock
@pytest.mark.asyncio
async def test_gemini_chat_chunk_upload(_mock_tiktoken):
    gemini_chat = _mock_tiktoken
    route = respx.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:streamGenerateContent"
    ).mock(return_value=httpx.Response(200, json={}))

    long_text = "a" * 520_000
    await gemini_chat([{"role": "user", "content": long_text}])
    import json
    payload = json.loads(route.calls[0].request.content.decode())
    assert payload["enable_chunked_upload"] is True


@respx.mock
@pytest.mark.asyncio
async def test_gemini_chat_client_error(_mock_tiktoken):
    gemini_chat = _mock_tiktoken
    respx.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:streamGenerateContent"
    ).mock(return_value=httpx.Response(400, json={"error": "bad"}))

    with pytest.raises(LLMApiError) as exc:
        await gemini_chat([{"role": "user", "content": "hi"}])
    assert exc.value.code == 400
    assert exc.value.vendor == "gemini"


@respx.mock
@pytest.mark.asyncio
async def test_gemini_chat_server_error_retries(monkeypatch, _mock_tiktoken):
    gemini_chat = _mock_tiktoken
    respx.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:streamGenerateContent"
    ).mock(side_effect=[httpx.Response(500, json={"error": "fail"})] * 5)

    sleeps = []

    async def fake_sleep(seconds):
        sleeps.append(seconds)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    with pytest.raises(LLMApiError) as exc:
        await gemini_chat([{"role": "user", "content": "hi"}])

    assert exc.value.code == 500
    assert len(sleeps) == 4


@pytest.mark.asyncio
async def test_gemini_chat_token_limit(_mock_tiktoken):
    gemini_chat = _mock_tiktoken
    over_limit = "a" * 1_000_001
    with pytest.raises(ValueError):
        await gemini_chat([{"role": "user", "content": over_limit}])
