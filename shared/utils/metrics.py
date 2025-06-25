from fastapi import FastAPI
from prometheus_client import Gauge, make_asgi_app

llm_daily_cost_usd = Gauge(
    "llm_daily_cost_usd", "Accumulated LLM cost in USD", ["vendor"]
)

_PRICING = {
    "gemini": {"prompt": 0.0005, "completion": 0.0015},
    "deepseek": {"prompt": 0.0001, "completion": 0.0002},
}

_daily_totals: dict[str, float] = {v: 0.0 for v in _PRICING}


def record_cost(
    prompt_tokens: int,
    completion_tokens: int,
    vendor: str,
) -> None:
    if vendor not in _PRICING:
        return
    prices = _PRICING[vendor]
    cost = (
        prompt_tokens * prices["prompt"]
        + completion_tokens * prices["completion"]  # noqa: E501
    )
    _daily_totals[vendor] += cost
    llm_daily_cost_usd.labels(vendor=vendor).set(_daily_totals[vendor])


def setup_metrics(app: FastAPI) -> None:
    app.mount("/metrics", make_asgi_app())
