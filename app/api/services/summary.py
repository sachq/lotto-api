from datetime import date

from sqlalchemy.orm import Session

from ..db import models


def get_draws(db: Session):
    return db.query(models.LottoDraw).all()


def get_draw_by_date(db: Session, draw_date: date):
    draws = db.query(models.LottoDraw).filter(
        models.LottoDraw.draw_date == draw_date).all()

    # if draws are found
    if draws is not None:
        return draws

    # return empty array if no draws are found
    return []
