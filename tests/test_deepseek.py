import asyncio
import importlib

import httpx
import pytest
import tiktoken

from shared.models.errors import LLMApiError


class DummyEncoding:
    def encode(self, text: str):
        return list(text)


@pytest.fixture(autouse=True)
def _mock_tiktoken(monkeypatch):
    monkeypatch.setattr(tiktoken, "get_encoding", lambda name: DummyEncoding())
    import shared.adapters.deepseek as ds

    importlib.reload(ds)
    return ds.deepseek_chat


class DummyClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def post(self, url, json=None):
        self.calls += 1
        resp = self.responses.pop(0)
        if isinstance(resp, Exception):
            raise resp
        return resp


@pytest.mark.asyncio
async def test_deepseek_chat_success(monkeypatch, _mock_tiktoken):
    deepseek_chat = _mock_tiktoken
    responses = [httpx.Response(200, json={"ok": True})]
    client = DummyClient(responses)
    monkeypatch.setattr(httpx, "AsyncClient", lambda **_: client)

    result = await deepseek_chat([{"role": "user", "content": "hi"}])
    assert result == {"ok": True}
    assert client.calls == 1


@pytest.mark.asyncio
async def test_deepseek_chat_client_error(monkeypatch, _mock_tiktoken):
    deepseek_chat = _mock_tiktoken
    responses = [httpx.Response(400, json={"error": "bad"})]
    client = DummyClient(responses)
    monkeypatch.setattr(httpx, "AsyncClient", lambda **_: client)

    with pytest.raises(LLMApiError) as exc:
        await deepseek_chat([{"role": "user", "content": "hi"}])
    assert exc.value.code == 400


@pytest.mark.asyncio
async def test_deepseek_chat_server_error_retries(monkeypatch, _mock_tiktoken):
    deepseek_chat = _mock_tiktoken
    responses = [httpx.Response(500, json={"error": "fail"}) for _ in range(5)]
    client = DummyClient(responses)
    monkeypatch.setattr(httpx, "AsyncClient", lambda **_: client)

    sleeps = []

    async def fake_sleep(seconds):
        sleeps.append(seconds)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    with pytest.raises(LLMApiError) as exc:
        await deepseek_chat([{"role": "user", "content": "hi"}])
    assert exc.value.code == 500
    assert len(sleeps) == 4
    assert client.calls == 5


@pytest.mark.asyncio
async def test_deepseek_chat_token_limit(monkeypatch, _mock_tiktoken):
    deepseek_chat = _mock_tiktoken
    over_limit = "a" * 65000
    with pytest.raises(ValueError):
        await deepseek_chat([{"role": "user", "content": over_limit}])
