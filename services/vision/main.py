from fastapi import APIRouter
from pydantic import BaseModel

from shared.models import VisionResponse

from . import image_loader, vision_tool

router = APIRouter(prefix="/v1/vision")


class ClassifyInput(BaseModel):
    image_id: str
    top_k: int | None = None


@router.post("/classify")
async def classify(payload: ClassifyInput):
    img = await image_loader.load(payload.image_id)
    labels, nsfw_flag = vision_tool.classify(img, payload.top_k or 5)
    response = VisionResponse(labels=labels, bbox=[], nsfw_flag=nsfw_flag)
    return response.model_dump()
