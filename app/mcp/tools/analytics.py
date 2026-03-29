import json
from collections import Counter

from mcp.types import Tool
from sqlalchemy import func

from app.api.db.models import LottoDraw, LottoType
from app.api.db.schemas import LottoTypeEnum
from app.api.services.prediction import LOTTO_CONFIG
from app.mcp.db import get_session


TOOLS = [
    Tool(
        name="get_number_frequencies",
        description="Get frequency counts for all lottery numbers of a given type",
        inputSchema={
            "type": "object",
            "properties": {
                "lotto_type": {"type": "string", "enum": ["powerball", "megamillion"], "description": "Lottery type"},
                "number_type": {"type": "string", "enum": ["main", "bonus"], "description": "Type of numbers (main 5 numbers or bonus/jackpot number)", "default": "main"},
            },
            "required": ["lotto_type"],
        },
    ),
    Tool(
        name="get_hot_cold_numbers",
        description="Get the most and least frequently drawn numbers",
        inputSchema={
            "type": "object",
            "properties": {
                "lotto_type": {"type": "string", "enum": ["powerball", "megamillion"], "description": "Lottery type"},
                "top_n": {"type": "integer", "description": "Number of hot/cold numbers to return (default 10)", "default": 10},
            },
            "required": ["lotto_type"],
        },
    ),
    Tool(
        name="get_draw_stats",
        description="Get summary statistics about stored draws (total count, date range, etc.)",
        inputSchema={
            "type": "object",
            "properties": {
                "lotto_type": {"type": "string", "enum": ["powerball", "megamillion"], "description": "Optional lottery type filter"},
            },
        },
    ),
]

DISPLAY_NAMES = {"powerball": "Powerball", "megamillion": "Megamillion"}


def _get_draws_for_type(db, lotto_type_enum):
    config = LOTTO_CONFIG[lotto_type_enum]
    return (
        db.query(LottoDraw)
        .join(LottoType)
        .filter(LottoType.name == config["display_name"], LottoDraw.is_active == True)
        .all()
    )


def _handle_get_number_frequencies(arguments: dict):
    lotto_type_enum = LottoTypeEnum(arguments["lotto_type"])
    number_type = arguments.get("number_type", "main")
    config = LOTTO_CONFIG[lotto_type_enum]

    with get_session() as db:
        draws = _get_draws_for_type(db, lotto_type_enum)
        counts = Counter()
        if number_type == "main":
            for draw in draws:
                for num in [draw.A, draw.B, draw.C, draw.D, draw.E]:
                    counts[num] += 1
            num_range = config["main_range"]
        else:
            for draw in draws:
                counts[draw.J] += 1
            num_range = config["bonus_range"]

        frequencies = {n: counts.get(n, 0) for n in range(num_range[0], num_range[1] + 1)}
        return json.dumps({
            "lotto_type": arguments["lotto_type"],
            "number_type": number_type,
            "total_draws": len(draws),
            "frequencies": dict(sorted(frequencies.items(), key=lambda x: x[1], reverse=True)),
        })


def _handle_get_hot_cold_numbers(arguments: dict):
    lotto_type_enum = LottoTypeEnum(arguments["lotto_type"])
    top_n = arguments.get("top_n", 10)
    config = LOTTO_CONFIG[lotto_type_enum]

    with get_session() as db:
        draws = _get_draws_for_type(db, lotto_type_enum)

        main_counts = Counter()
        bonus_counts = Counter()
        for draw in draws:
            for num in [draw.A, draw.B, draw.C, draw.D, draw.E]:
                main_counts[num] += 1
            bonus_counts[draw.J] += 1

        # Ensure all numbers in range appear
        for n in range(config["main_range"][0], config["main_range"][1] + 1):
            main_counts.setdefault(n, 0)
        for n in range(config["bonus_range"][0], config["bonus_range"][1] + 1):
            bonus_counts.setdefault(n, 0)

        main_sorted = sorted(main_counts.items(), key=lambda x: x[1], reverse=True)
        bonus_sorted = sorted(bonus_counts.items(), key=lambda x: x[1], reverse=True)

        return json.dumps({
            "lotto_type": arguments["lotto_type"],
            "total_draws": len(draws),
            "main_numbers": {
                "hot": [{"number": n, "count": c} for n, c in main_sorted[:top_n]],
                "cold": [{"number": n, "count": c} for n, c in main_sorted[-top_n:]],
            },
            "bonus_numbers": {
                "hot": [{"number": n, "count": c} for n, c in bonus_sorted[:top_n]],
                "cold": [{"number": n, "count": c} for n, c in bonus_sorted[-top_n:]],
            },
        })


def _handle_get_draw_stats(arguments: dict):
    lotto_type = arguments.get("lotto_type")

    with get_session() as db:
        if lotto_type:
            display_name = DISPLAY_NAMES[lotto_type]
            query = (
                db.query(
                    func.count(LottoDraw.id).label("total"),
                    func.min(LottoDraw.draw_date).label("earliest"),
                    func.max(LottoDraw.draw_date).label("latest"),
                )
                .join(LottoType)
                .filter(LottoType.name == display_name, LottoDraw.is_active == True)
            )
            row = query.one()
            return json.dumps({
                "lotto_type": lotto_type,
                "total_draws": row.total,
                "earliest_draw": str(row.earliest) if row.earliest else None,
                "latest_draw": str(row.latest) if row.latest else None,
            })
        else:
            stats = []
            for lt_enum in LottoTypeEnum:
                config = LOTTO_CONFIG[lt_enum]
                row = (
                    db.query(
                        func.count(LottoDraw.id).label("total"),
                        func.min(LottoDraw.draw_date).label("earliest"),
                        func.max(LottoDraw.draw_date).label("latest"),
                    )
                    .join(LottoType)
                    .filter(LottoType.name == config["display_name"], LottoDraw.is_active == True)
                    .one()
                )
                stats.append({
                    "lotto_type": lt_enum.value,
                    "total_draws": row.total,
                    "earliest_draw": str(row.earliest) if row.earliest else None,
                    "latest_draw": str(row.latest) if row.latest else None,
                })
            return json.dumps(stats)


HANDLERS = {
    "get_number_frequencies": _handle_get_number_frequencies,
    "get_hot_cold_numbers": _handle_get_hot_cold_numbers,
    "get_draw_stats": _handle_get_draw_stats,
}
