from fastapi import APIRouter

from app.api.endpoints import summary, prediction

router = APIRouter()

router.include_router(summary.router, prefix="/summary", tags=["summary"])
router.include_router(prediction.router, prefix="/prediction", tags=["prediction"])
