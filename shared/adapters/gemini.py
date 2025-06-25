import asyncio
import random
from typing import Any

import httpx
import tiktoken

from shared.models.errors import LLMApiError

API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent"  # noqa: E501
TOKEN_LIMIT = 1_000_000
CHUNK_TRIGGER = 512_000
ENCODING = tiktoken.get_encoding("cl100k_base")


async def gemini_chat(
    messages: list[dict],
    model: str = "gemini-1.5-pro",
    tools: list | None = None,
    **kwargs: Any,
) -> dict:
    token_count = sum(
        len(ENCODING.encode(m.get("content", ""))) for m in messages
    )  # noqa: E501
    if token_count > TOKEN_LIMIT:
        raise ValueError("input exceeds 1M token limit")

    if token_count > CHUNK_TRIGGER:
        kwargs.setdefault("enable_chunked_upload", True)

    kwargs.setdefault("response_mime_type", "application/json")

    payload: dict[str, Any] = {"contents": messages, **kwargs}
    if tools is not None:
        payload["tools"] = tools

    url = API_ENDPOINT.format(model=model)
    max_retries = 4

    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload)
            if 200 <= resp.status_code < 300:
                return resp.json()
            if 400 <= resp.status_code < 500:
                raise LLMApiError(
                    code=resp.status_code, message=resp.text, vendor="gemini"
                )
            if attempt == max_retries:
                raise LLMApiError(
                    code=resp.status_code, message=resp.text, vendor="gemini"
                )
        except httpx.HTTPError as e:
            if attempt == max_retries:
                raise LLMApiError(code=0, message=str(e), vendor="gemini")
        wait = random.uniform(0, 2**attempt)
        await asyncio.sleep(wait)

    raise LLMApiError(code=0, message="unknown error", vendor="gemini")
