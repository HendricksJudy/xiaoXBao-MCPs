from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def add_safety_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def _safety(request: Request, call_next):
        if request.headers.get("x-block") == "1":
            return JSONResponse(status_code=400, content={"detail": "blocked"})
        return await call_next(request)
