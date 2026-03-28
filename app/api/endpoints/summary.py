from datetime import date
from typing import Optional

from fastapi import Depends, APIRouter, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.db import schemas
from app.api.db import session
from app.api.services import summary

router = APIRouter()


@router.get("/draws", response_model=list[schemas.LottoDraw])
def get_all_draws(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(session.get_db)
):
    """
    Get all lottery draws with pagination.
    Returns an empty list if no draws are found (not 404).
    """
    return summary.get_draws(db, skip=skip, limit=limit)


@router.get("/draws/{draw_date}", response_model=list[schemas.LottoDraw])
def get_draw_by_date(draw_date: date, db: Session = Depends(session.get_db)):
    """
    Get all draws for a specific date.
    Returns 404 only for a specific date query with no results.
    """
    all_draws = summary.get_draw_by_date(db, draw_date)
    if not all_draws:
        raise HTTPException(status_code=404,
                            detail=f'No draws found for the date: {draw_date}')
    return all_draws
