from fastapi import APIRouter
from .endpoints import summary
from app.config import get_settings

router = APIRouter()
settings = get_settings()

router.include_router(summary.router, prefix=settings.API_VERSION_PREFIX)
