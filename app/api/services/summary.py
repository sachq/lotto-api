from sqlalchemy.orm import Session

from ..db import models


def get_draws(db: Session):
    return db.query(models.LottoDraw).all()


def get_draw(db: Session, draw_id: int):
    return db.query(models.LottoDraw).filter(
        models.LottoDraw.lotto_type_id == draw_id).first()
