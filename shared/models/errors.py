from dataclasses import dataclass
from fastapi.responses import JSONResponse


@dataclass(init=False)
class LLMApiError(Exception):
    """Error returned by LLM providers."""

    vendor: str
    code: int
    message: str
    retriable: bool

    def __init__(self, *args, **kwargs):
        """Support both new and legacy initialization styles."""
        if args and isinstance(args[0], int):
            # legacy: LLMApiError(code, message, vendor="...", retriable=False)
            self.code = args[0]
            self.message = args[1] if len(args) > 1 else kwargs.get("message", "")
            self.vendor = kwargs.get("vendor", "deepseek")
            self.retriable = kwargs.get("retriable", False)
        else:
            # new: LLMApiError(vendor, code, message, retriable=False)
            self.vendor = args[0] if args else kwargs.get("vendor", "deepseek")
            self.code = args[1] if len(args) > 1 else kwargs.get("code", 0)
            self.message = args[2] if len(args) > 2 else kwargs.get("message", "")
            self.retriable = args[3] if len(args) > 3 else kwargs.get("retriable", False)
        super().__init__(self.message)


@dataclass
class BusinessError(Exception):
    http_status: int
    detail: str

    def to_response(self) -> JSONResponse:
        """Convert the error into a FastAPI JSON response."""
        return JSONResponse(status_code=self.http_status, content={"detail": self.detail})
