from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from app.api.db import crud, schemas
from app.api.db import session

router = APIRouter()


@router.get("/draws", response_model=list[schemas.LottoDraw])
def get_users(db: Session = Depends(session.get_db)):
    return crud.get_draws(db)


@router.get("/draws/{lotto_type_id}", response_model=schemas.LottoDraw)
def get_user(lotto_type_id: int, db: Session = Depends(session.get_db)):
    return crud.get_draw(db, lotto_type_id)
