import logging
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio import Redis

from .metrics import llm_daily_cost_usd


async def check_budget(redis: Redis) -> None:
    day_cost = 0.0
    for metric in llm_daily_cost_usd.collect():
        for sample in metric.samples:
            day_cost += sample.value
    limit = int(os.getenv("DAILY_BUDGET_USD", "100"))
    if day_cost > limit:
        logging.warning("LLM spend %.2f exceeds budget %.2f", day_cost, limit)
        await redis.set("COST_SENSITIVE", "true")


scheduler = AsyncIOScheduler()


def start(redis: Redis) -> None:
    scheduler.add_job(check_budget, "interval", hours=1, args=[redis])
    scheduler.start()
