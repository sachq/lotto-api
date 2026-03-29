import math
from datetime import date

from sqlalchemy.orm import Session, joinedload

from ..db import models


def get_draws(db: Session, page: int = 1, per_page: int = 50):
    base_query = (
        db.query(models.LottoDraw)
        .filter(models.LottoDraw.is_active == True)
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

    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total_items": total_items,
        "total_pages": total_pages,
    }


def get_draw_by_date(db: Session, draw_date: date):
    return (
        db.query(models.LottoDraw)
        .options(joinedload(models.LottoDraw.lotto_type))
        .filter(
            models.LottoDraw.draw_date == draw_date,
            models.LottoDraw.is_active == True
        )
        .all()
    )
