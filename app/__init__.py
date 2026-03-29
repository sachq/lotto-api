from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api import router as api_router
from .config import get_settings
from .mcp.server import session_manager


@asynccontextmanager
async def lifespan(app):
    async with session_manager.run():
        yield


# Initialize FastAPI Application
_fastapi = FastAPI(lifespan=lifespan)

# Get Environment Settings
settings = get_settings()

_fastapi.include_router(api_router, prefix=settings.API_PREFIX)


async def app(scope, receive, send):
    """ASGI entrypoint that routes /mcp to the MCP server, everything else to FastAPI."""
    if scope["type"] == "http" and scope["path"].startswith("/mcp"):
        scope["path"] = scope["path"][4:] or "/"
        await session_manager.handle_request(scope, receive, send)
    else:
        await _fastapi(scope, receive, send)
