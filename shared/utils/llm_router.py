import time
from typing import Any

from prometheus_client import Counter

from shared.adapters.deepseek import deepseek_chat
from shared.adapters.gemini import gemini_chat


llm_calls_total = Counter("llm_calls_total", "Total number of LLM calls", ["vendor"])

_BREAKER = {
    "gemini": {"failures": 0, "until": 0.0},
    "deepseek": {"failures": 0, "until": 0.0},
}


async def route_llm(
    domain: str,
    messages: list[dict],
    ctx_tokens: int,
    cost_sensitive: bool = False,
) -> dict:
    """Route request to an LLM provider based on heuristics with breaker."""
    vendor: str
    model: str | None = None

    if ctx_tokens > 64000:
        vendor = "gemini"
    elif cost_sensitive or domain == "oncology_kb":
        vendor = "deepseek"
    else:
        vendor = "gemini"
        model = "gemini-1.5-flash"

    now = time.monotonic()
    state = _BREAKER[vendor]
    if state["until"] > now:
        vendor = "deepseek" if vendor == "gemini" else "gemini"
        model = None
        state = _BREAKER[vendor]

    try:
        if vendor == "gemini":
            if model is None:
                result = await gemini_chat(messages)
            else:
                result = await gemini_chat(messages, model=model)
        else:
            result = await deepseek_chat(messages)
        state["failures"] = 0
        return result
    except Exception:
        state["failures"] += 1
        if state["failures"] >= 3:
            state["until"] = time.monotonic() + 120
            state["failures"] = 0
        raise
    finally:
        llm_calls_total.labels(vendor=vendor).inc()

