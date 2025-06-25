import asyncio
import random
from typing import Any

import httpx
import tiktoken

from shared.models.errors import LLMApiError

API_URL = "https://api.deepseek.com/chat/completions"
TOKEN_LIMIT = 64_000
ENCODING = tiktoken.get_encoding("cl100k_base")


async def deepseek_chat(
    messages: list[dict], model: str = "deepseek-chat-v3-0324", **kwargs: Any
) -> dict:
    token_count = sum(
        len(ENCODING.encode(m.get("content", ""))) for m in messages
    )  # noqa: E501
    if token_count > TOKEN_LIMIT:
        raise ValueError("input exceeds 64k token limit")

    payload = {"model": model, "messages": messages, **kwargs}
    max_retries = 4

    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(API_URL, json=payload)
            if 200 <= resp.status_code < 300:
                return resp.json()
            if 400 <= resp.status_code < 500:
                raise LLMApiError(code=resp.status_code, message=resp.text)
            # 5xx
            if attempt == max_retries:
                raise LLMApiError(code=resp.status_code, message=resp.text)
        except httpx.HTTPError as e:
            if attempt == max_retries:
                raise LLMApiError(code=0, message=str(e))
        wait = random.uniform(0, 2**attempt)
        await asyncio.sleep(wait)

    raise LLMApiError(code=0, message="unknown error")
