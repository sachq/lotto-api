import random
from collections import Counter
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.api.db.models import LottoDraw, LottoType
from app.api.db.schemas import LottoTypeEnum

LOTTO_CONFIG = {
    LottoTypeEnum.powerball: {
        "display_name": "Powerball",
        "main_range": (1, 69),
        "bonus_range": (1, 26),
        "draw_days": {0, 2, 5},  # Monday, Wednesday, Saturday
    },
    LottoTypeEnum.megamillion: {
        "display_name": "Megamillion",
        "main_range": (1, 70),
        "bonus_range": (1, 25),
        "draw_days": {1, 4},  # Tuesday, Friday
    },
}


def get_next_draw_date(lotto_type: LottoTypeEnum) -> date:
    draw_days = LOTTO_CONFIG[lotto_type]["draw_days"]
    today = date.today()
    for i in range(7):
        candidate = today + timedelta(days=i)
        if candidate.weekday() in draw_days:
            return candidate


def _get_frequency_weights(db: Session, lotto_type: LottoTypeEnum):
    config = LOTTO_CONFIG[lotto_type]
    main_lo, main_hi = config["main_range"]
    bonus_lo, bonus_hi = config["bonus_range"]

    draws = (
        db.query(LottoDraw)
        .join(LottoType)
        .filter(
            LottoType.name == config["display_name"],
            LottoDraw.is_active == True
        )
        .all()
    )

    main_counts = Counter()
    bonus_counts = Counter()

    for draw in draws:
        for num in [draw.A, draw.B, draw.C, draw.D, draw.E]:
            main_counts[num] += 1
        bonus_counts[draw.J] += 1

    # Build weight lists — every number gets at least a weight of 1
    main_numbers = list(range(main_lo, main_hi + 1))
    main_weights = [main_counts.get(n, 0) + 1 for n in main_numbers]

    bonus_numbers = list(range(bonus_lo, bonus_hi + 1))
    bonus_weights = [bonus_counts.get(n, 0) + 1 for n in bonus_numbers]

    return main_numbers, main_weights, bonus_numbers, bonus_weights


def generate_prediction(db: Session, lotto_type: LottoTypeEnum) -> dict:
    config = LOTTO_CONFIG[lotto_type]
    main_numbers, main_weights, bonus_numbers, bonus_weights = \
        _get_frequency_weights(db, lotto_type)

    # Weighted selection of 5 unique main numbers
    selected = []
    available = list(zip(main_numbers, main_weights))
    for _ in range(5):
        nums, weights = zip(*available)
        pick = random.choices(nums, weights=weights, k=1)[0]
        selected.append(pick)
        available = [(n, w) for n, w in available if n != pick]

    bonus_number = random.choices(bonus_numbers, weights=bonus_weights, k=1)[0]

    return {
        "lotto_type": config["display_name"],
        "numbers": sorted(selected),
        "bonus_number": bonus_number,
        "next_draw_date": get_next_draw_date(lotto_type),
    }
