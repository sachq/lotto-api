from sqlalchemy.orm import Session

from . import models


def get_users(db: Session):
    return db.query(models.LottoDraw).all()


def get_user(db: Session, draw_id: int):
    return db.query(models.LottoDraw).filter(
        models.LottoDraw.id == draw_id).first()
