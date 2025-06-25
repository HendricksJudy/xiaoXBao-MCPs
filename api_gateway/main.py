from fastapi import FastAPI

from services.oncology_kb.main import router as router_oncology
from services.psychology.main import router as router_psychology
from services.radiology.main import router as router_radiology
from services.vision.main import router as router_vision
from shared.utils import metrics, safety_middleware

app = FastAPI()

safety_middleware.add_safety_middleware(app)
metrics.setup_metrics(app)

app.include_router(router_psychology)
app.include_router(router_oncology)
app.include_router(router_radiology)
app.include_router(router_vision)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
