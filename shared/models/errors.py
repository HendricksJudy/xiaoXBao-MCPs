from dataclasses import dataclass


@dataclass
class LLMApiError(Exception):
    code: int
    message: str
    vendor: str = "deepseek"
