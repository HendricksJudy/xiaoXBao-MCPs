"""Simple regex based entity extractor stub."""

import re


async def extract_entities(text: str) -> list[str]:
    pattern = r"[A-Za-z]+"
    return re.findall(pattern, text)
