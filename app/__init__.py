from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api import router as api_router
from .config import get_settings
from .mcp.server import session_manager, create_http_app


@asynccontextmanager
async def lifespan(app):
    async with session_manager.run():
        yield


# Initialize FastAPI Application
app = FastAPI(lifespan=lifespan)

# Get Environment Settings
settings = get_settings()

app.include_router(api_router, prefix=settings.API_PREFIX)
app.mount("/mcp", create_http_app())
