import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import tiktoken  # noqa: E402


class DummyEncoding:
    def encode(self, text: str):
        return list(text)


tiktoken.get_encoding = lambda name: DummyEncoding()

import shared.adapters.deepseek  # noqa: E402,F401
import shared.adapters.gemini  # noqa: E402,F401
