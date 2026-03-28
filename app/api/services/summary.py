from datetime import date
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from ..db import models


def get_draws(db: Session, skip: int = 0, limit: int = 100):
    """
    Get all active lotto draws with pagination.
    :param db: Database session
    :param skip: Number of records to skip (offset)
    :param limit: Maximum number of records to return
    :return: List of LottoDraw objects
    """
    return (
        db.query(models.LottoDraw)
        .options(joinedload(models.LottoDraw.lotto_type))
        .filter(models.LottoDraw.is_active == True)
        .order_by(models.LottoDraw.draw_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_draw_by_date(db: Session, draw_date: date):
    """
    Get all active draws for a specific date.
    :param db: Database session
    :param draw_date: Date to filter by
    :return: List of LottoDraw objects
    """
    return (
        db.query(models.LottoDraw)
        .options(joinedload(models.LottoDraw.lotto_type))
        .filter(
            models.LottoDraw.draw_date == draw_date,
            models.LottoDraw.is_active == True
        )
        .all()
    )
