import pytest

from shared.utils import budget_guard, metrics


class DummyRedis:
    def __init__(self):
        self.values = {}

    async def set(self, key, value):
        self.values[key] = value


@pytest.mark.asyncio
async def test_budget_guard(monkeypatch):
    class DummyGauge:
        def collect(self):
            class M:
                samples = [type("S", (), {"value": 150.0})]

            return [M()]

    monkeypatch.setattr(metrics, "llm_daily_cost_usd", DummyGauge())
    monkeypatch.setattr(
        budget_guard,
        "llm_daily_cost_usd",
        metrics.llm_daily_cost_usd,
    )
    redis = DummyRedis()
    await budget_guard.check_budget(redis)
    assert redis.values["COST_SENSITIVE"] == "true"
