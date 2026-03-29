import json
import math
from datetime import date

from mcp.types import Tool
from sqlalchemy.orm import joinedload

from app.api.db import models
from app.api.db.schemas import LottoDraw as LottoDrawSchema
from app.api.services.summary import get_draws, get_draw_by_date
from app.mcp.db import get_session


def _serialize_draw(draw):
    return LottoDrawSchema.model_validate(draw).model_dump(mode="json")


TOOLS = [
    Tool(
        name="get_draws",
        description="Get paginated historical lottery draws (both Powerball and Megamillion)",
        inputSchema={
            "type": "object",
            "properties": {
                "page": {"type": "integer", "description": "Page number (default 1)", "default": 1},
                "per_page": {"type": "integer", "description": "Items per page (default 50, max 500)", "default": 50},
            },
        },
    ),
    Tool(
        name="get_draws_by_date",
        description="Get all lottery draws for a specific date",
        inputSchema={
            "type": "object",
            "properties": {
                "draw_date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
            },
            "required": ["draw_date"],
        },
    ),
    Tool(
        name="get_draws_by_type",
        description="Get paginated draws filtered by lottery type",
        inputSchema={
            "type": "object",
            "properties": {
                "lotto_type": {"type": "string", "enum": ["powerball", "megamillion"], "description": "Lottery type"},
                "page": {"type": "integer", "description": "Page number (default 1)", "default": 1},
                "per_page": {"type": "integer", "description": "Items per page (default 50, max 500)", "default": 50},
            },
            "required": ["lotto_type"],
        },
    ),
    Tool(
        name="get_draws_in_range",
        description="Get draws within a date range, optionally filtered by lottery type",
        inputSchema={
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"},
                "lotto_type": {"type": "string", "enum": ["powerball", "megamillion"], "description": "Optional lottery type filter"},
            },
            "required": ["start_date", "end_date"],
        },
    ),
]

DISPLAY_NAMES = {"powerball": "Powerball", "megamillion": "Megamillion"}


def _handle_get_draws(arguments: dict):
    page = arguments.get("page", 1)
    per_page = min(arguments.get("per_page", 50), 500)
    with get_session() as db:
        result = get_draws(db, page=page, per_page=per_page)
        return json.dumps({
            "items": [_serialize_draw(d) for d in result["items"]],
            "page": result["page"],
            "per_page": result["per_page"],
            "total_items": result["total_items"],
            "total_pages": result["total_pages"],
        }, default=str)


def _handle_get_draws_by_date(arguments: dict):
    draw_date = date.fromisoformat(arguments["draw_date"])
    with get_session() as db:
        draws = get_draw_by_date(db, draw_date)
        return json.dumps([_serialize_draw(d) for d in draws], default=str)


def _handle_get_draws_by_type(arguments: dict):
    lotto_type = arguments["lotto_type"]
    display_name = DISPLAY_NAMES[lotto_type]
    page = arguments.get("page", 1)
    per_page = min(arguments.get("per_page", 50), 500)

    with get_session() as db:
        base_query = (
            db.query(models.LottoDraw)
            .join(models.LottoType)
            .filter(
                models.LottoType.name == display_name,
                models.LottoDraw.is_active == True,
            )
        )
        total_items = base_query.count()
        total_pages = math.ceil(total_items / per_page) if total_items > 0 else 0
        items = (
            base_query
            .options(joinedload(models.LottoDraw.lotto_type))
            .order_by(models.LottoDraw.draw_date.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return json.dumps({
            "items": [_serialize_draw(d) for d in items],
            "page": page,
            "per_page": per_page,
            "total_items": total_items,
            "total_pages": total_pages,
        }, default=str)


def _handle_get_draws_in_range(arguments: dict):
    start = date.fromisoformat(arguments["start_date"])
    end = date.fromisoformat(arguments["end_date"])
    lotto_type = arguments.get("lotto_type")

    with get_session() as db:
        query = (
            db.query(models.LottoDraw)
            .options(joinedload(models.LottoDraw.lotto_type))
            .filter(
                models.LottoDraw.draw_date >= start,
                models.LottoDraw.draw_date <= end,
                models.LottoDraw.is_active == True,
            )
        )
        if lotto_type:
            display_name = DISPLAY_NAMES[lotto_type]
            query = query.join(models.LottoType).filter(
                models.LottoType.name == display_name
            )
        draws = query.order_by(models.LottoDraw.draw_date.desc()).all()
        return json.dumps([_serialize_draw(d) for d in draws], default=str)


HANDLERS = {
    "get_draws": _handle_get_draws,
    "get_draws_by_date": _handle_get_draws_by_date,
    "get_draws_by_type": _handle_get_draws_by_type,
    "get_draws_in_range": _handle_get_draws_in_range,
}
