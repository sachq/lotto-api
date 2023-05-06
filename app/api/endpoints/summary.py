from datetime import date

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.api.db import schemas
from app.api.db import session
from app.api.services import summary

router = APIRouter()


@router.get("/draws", response_model=list[schemas.LottoDraw])
def get_user(draw_date: date, db: Session = Depends(session.get_db)):
    all_draws = summary.get_draw_by_date(db, draw_date)
    if not all_draws:
        raise HTTPException(status_code=404,
                            detail=f'No draws found for the date: {draw_date}')
    return all_draws
