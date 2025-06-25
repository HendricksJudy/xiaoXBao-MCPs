"""Image loading stub."""

from shared.models import BusinessError


async def load(image_id: str) -> bytes:
    if image_id == "missing":
        raise BusinessError(404, "Image not found")
    return b"fakeimage"
