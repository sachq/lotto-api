from fastapi import APIRouter

from app.api.endpoints import summary

router = APIRouter()

router.include_router(summary.router, prefix="/summary", tags=["summary"])
