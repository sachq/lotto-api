from datetime import date
from typing import Optional

from fastapi import Depends, APIRouter, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.db import schemas
from app.api.db import session
from app.api.services import summary

router = APIRouter()


@router.get("/draws", response_model=schemas.PaginatedDraws)
def get_all_draws(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=500, description="Items per page"),
    db: Session = Depends(session.get_db)
):
    return summary.get_draws(db, page=page, per_page=per_page)


@router.get("/draws/{draw_date}", response_model=list[schemas.LottoDraw])
def get_draw_by_date(draw_date: date, db: Session = Depends(session.get_db)):
    all_draws = summary.get_draw_by_date(db, draw_date)
    if not all_draws:
        raise HTTPException(status_code=404,
                            detail=f'No draws found for the date: {draw_date}')
    return all_draws
