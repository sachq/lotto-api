import random
from collections import Counter
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy.orm import Session

from app.api.db.models import LottoDraw, LottoType
from app.api.db.schemas import LottoTypeEnum

ET = timezone(timedelta(hours=-4))

LOTTO_CONFIG = {
    LottoTypeEnum.powerball: {
        "display_name": "Powerball",
        "main_range": (1, 69),
        "bonus_range": (1, 26),
        "draw_days": {0, 2, 5},  # Monday, Wednesday, Saturday
        "draw_time": time(22, 59, tzinfo=ET),  # 10:59 PM ET
    },
    LottoTypeEnum.megamillion: {
        "display_name": "Megamillion",
        "main_range": (1, 70),
        "bonus_range": (1, 25),
        "draw_days": {1, 4},  # Tuesday, Friday
        "draw_time": time(23, 0, tzinfo=ET),  # 11:00 PM ET
    },
}


def get_next_draw_date(lotto_type: LottoTypeEnum) -> date:
    config = LOTTO_CONFIG[lotto_type]
    draw_days = config["draw_days"]
    draw_time = config["draw_time"]
    now = datetime.now(ET)
    today = now.date()

    for i in range(7):
        candidate = today + timedelta(days=i)
        if candidate.weekday() in draw_days:
            # If today is a draw day but the draw time has passed, skip to next
            if candidate == today and now.timetz() >= draw_time:
                continue
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


def _validate_draw_date(draw_date: date, lotto_type: LottoTypeEnum) -> None:
    config = LOTTO_CONFIG[lotto_type]
    if draw_date.weekday() not in config["draw_days"]:
        day_names = {0: "Monday", 1: "Tuesday", 2: "Wednesday",
                     3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
        valid_days = ", ".join(day_names[d] for d in sorted(config["draw_days"]))
        raise ValueError(
            f"{draw_date} is not a valid {config['display_name']} draw day. "
            f"Valid days: {valid_days}"
        )


def generate_prediction(db: Session, lotto_type: LottoTypeEnum,
                        draw_date: date = None, count: int = 1) -> dict:
    config = LOTTO_CONFIG[lotto_type]

    if draw_date is None:
        draw_date = get_next_draw_date(lotto_type)
    else:
        _validate_draw_date(draw_date, lotto_type)

    main_numbers, main_weights, bonus_numbers, bonus_weights = \
        _get_frequency_weights(db, lotto_type)

    draw_time = config["draw_time"]
    seed_dt = datetime.combine(draw_date, draw_time)

    combinations = []
    for i in range(count):
        # Each combination gets a unique but deterministic seed
        rng = random.Random(hash((seed_dt.isoformat(), lotto_type.value, i)))

        selected = []
        available = list(zip(main_numbers, main_weights))
        for _ in range(5):
            nums, weights = zip(*available)
            pick = rng.choices(nums, weights=weights, k=1)[0]
            selected.append(pick)
            available = [(n, w) for n, w in available if n != pick]

        bonus_number = rng.choices(bonus_numbers, weights=bonus_weights, k=1)[0]
        combinations.append({
            "numbers": sorted(selected),
            "bonus_number": bonus_number,
        })

    return {
        "lotto_type": config["display_name"],
        "draw_date": draw_date,
        "combinations": combinations,
    }
