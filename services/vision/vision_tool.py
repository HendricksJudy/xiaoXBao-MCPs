"""Vision classification stub."""

import random


def classify(img: bytes, top_k: int) -> tuple[list[dict], bool]:
    labels = [
        {"name": "cat", "confidence": 0.92},
        {"name": "dog", "confidence": 0.5},
    ][:top_k]
    nsfw_score = random.random() * 0.2
    return labels, nsfw_score > 0.18
