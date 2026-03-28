from fastapi import APIRouter
from .endpoints import router as endpoints_router
from app.config import get_settings

router = APIRouter()
settings = get_settings()

router.include_router(endpoints_router, prefix=settings.API_VERSION_PREFIX)
