from fastapi import FastAPI

from .api import router as api_router
from .config import get_settings

# Initialize FastAPI Application
app = FastAPI()

# Get Environment Settings
settings = get_settings()

app.include_router(api_router, prefix=settings.API_PREFIX)
