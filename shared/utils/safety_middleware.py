import json
import logging
import re
from typing import Any, Callable

import tiktoken
from fastapi import FastAPI, Request, Response

PII_RE = re.compile(
    r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|\+?\d[\d-]{7,}\d)"
)
ENCODING = tiktoken.get_encoding("cl100k_base")
TOKEN_LIMIT = 512


def _scrub(obj: Any) -> Any:
    if isinstance(obj, str):
        return PII_RE.sub("[REDACTED]", obj)
    if isinstance(obj, list):
        return [_scrub(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _scrub(v) for k, v in obj.items()}
    return obj


def add_safety_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def _safety(request: Request, call_next: Callable[[Request], Any]):
        raw_body = await request.body()
        new_body = raw_body
        if raw_body:
            try:
                data = json.loads(raw_body.decode())
                scrubbed = _scrub(data)
                new_body = json.dumps(scrubbed).encode()
            except Exception as exc:  # pragma: no cover - bad input
                logging.warning("failed to parse body for PII scrub: %s", exc)
        request = Request(
            request.scope, lambda: {"type": "http.request", "body": new_body}
        )

        response: Response = await call_next(request)

        body = b"".join([chunk async for chunk in response.body_iterator])
        content_type = response.media_type or "application/json"
        try:
            data = json.loads(body.decode())
            scrubbed = _scrub(data)
            body_text = json.dumps(scrubbed)
        except Exception:
            body_text = _scrub(body.decode()) if body else ""

        tokens = ENCODING.encode(body_text)
        if len(tokens) > TOKEN_LIMIT:
            body_text = ENCODING.decode(tokens[:TOKEN_LIMIT]) + "..."
        return Response(
            content=body_text,
            status_code=response.status_code,
            media_type=content_type,
            headers=dict(response.headers),
        )
