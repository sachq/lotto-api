import json
from datetime import date

from mcp.types import Tool

from app.api.db.schemas import LottoTypeEnum
from app.api.services.prediction import (
    generate_prediction,
    get_next_draw_date,
)
from app.mcp.db import get_session


TOOLS = [
    Tool(
        name="generate_prediction",
        description="Generate frequency-weighted lottery number predictions based on historical data",
        inputSchema={
            "type": "object",
            "properties": {
                "lotto_type": {"type": "string", "enum": ["powerball", "megamillion"], "description": "Lottery type"},
                "draw_date": {"type": "string", "description": "Draw date in YYYY-MM-DD format (defaults to next draw day)"},
                "count": {"type": "integer", "description": "Number of combinations to generate (1-10, default 1)", "default": 1},
            },
            "required": ["lotto_type"],
        },
    ),
    Tool(
        name="get_next_draw_date",
        description="Get the next upcoming draw date for a lottery type",
        inputSchema={
            "type": "object",
            "properties": {
                "lotto_type": {"type": "string", "enum": ["powerball", "megamillion"], "description": "Lottery type"},
            },
            "required": ["lotto_type"],
        },
    ),
]


def _handle_generate_prediction(arguments: dict):
    lotto_type = LottoTypeEnum(arguments["lotto_type"])
    draw_date = date.fromisoformat(arguments["draw_date"]) if arguments.get("draw_date") else None
    count = min(arguments.get("count", 1), 10)

    with get_session() as db:
        result = generate_prediction(db, lotto_type, draw_date=draw_date, count=count)
        return json.dumps(result, default=str)


def _handle_get_next_draw_date(arguments: dict):
    lotto_type = LottoTypeEnum(arguments["lotto_type"])
    next_date = get_next_draw_date(lotto_type)
    return json.dumps({"lotto_type": arguments["lotto_type"], "next_draw_date": str(next_date)})


HANDLERS = {
    "generate_prediction": _handle_generate_prediction,
    "get_next_draw_date": _handle_get_next_draw_date,
}
