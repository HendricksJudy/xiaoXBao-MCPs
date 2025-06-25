import importlib
import types

import pytest

from shared.models.errors import LLMApiError


class DummyCounterInstance:
    def __init__(self, counts, vendor):
        self.counts = counts
        self.vendor = vendor

    def inc(self):
        self.counts[self.vendor] = self.counts.get(self.vendor, 0) + 1


class DummyCounter:
    def __init__(self):
        self.counts = {}

    def labels(self, vendor):
        return DummyCounterInstance(self.counts, vendor)


@pytest.fixture
def router(monkeypatch):
    dummy_counter = DummyCounter()
    monkeypatch.setattr(
        importlib.import_module("prometheus_client"), "Counter", lambda *a, **k: dummy_counter
    )
    module = importlib.reload(importlib.import_module("shared.utils.llm_router"))
    return module, dummy_counter


@pytest.mark.asyncio
async def test_routing_rules(monkeypatch, router):
    module, counter = router

    async def fake_gemini(messages, model="gemini-1.5-pro"):
        return {"vendor": "gemini", "model": model}

    async def fake_deepseek(messages):
        return {"vendor": "deepseek"}

    monkeypatch.setattr(module, "gemini_chat", fake_gemini)
    monkeypatch.setattr(module, "deepseek_chat", fake_deepseek)

    res = await module.route_llm("general", [], 10)
    assert res == {"vendor": "gemini", "model": "gemini-1.5-flash"}

    res = await module.route_llm("general", [], 65000)
    assert res == {"vendor": "gemini", "model": "gemini-1.5-pro"}

    res = await module.route_llm("oncology_kb", [], 10)
    assert res == {"vendor": "deepseek"}

    res = await module.route_llm("general", [], 10, cost_sensitive=True)
    assert res == {"vendor": "deepseek"}

    assert counter.counts["gemini"] == 2
    assert counter.counts["deepseek"] == 2


@pytest.mark.asyncio
async def test_circuit_breaker(monkeypatch, router):
    module, counter = router

    time_vals = [0]

    def fake_monotonic():
        return time_vals[0]

    monkeypatch.setattr(module.time, "monotonic", fake_monotonic)

    async def fail_gemini(messages, model="gemini-1.5-pro"):
        raise LLMApiError(500, "fail", vendor="gemini")

    async def ok_deepseek(messages):
        return {"ok": True}

    monkeypatch.setattr(module, "gemini_chat", fail_gemini)
    monkeypatch.setattr(module, "deepseek_chat", ok_deepseek)

    for _ in range(3):
        with pytest.raises(LLMApiError):
            await module.route_llm("general", [], 10)

    assert module._BREAKER["gemini"]["until"] == pytest.approx(120)

    res = await module.route_llm("general", [], 10)
    assert res == {"ok": True}
    assert counter.counts["deepseek"] == 1

    time_vals[0] = 121
    async def ok_gemini(messages, model="gemini-1.5-pro"):
        return {"ok": "gemini"}

    monkeypatch.setattr(module, "gemini_chat", ok_gemini)

    res = await module.route_llm("general", [], 10)
    assert res == {"ok": "gemini"}

