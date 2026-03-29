from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.db import schemas, session
from app.api.services import prediction

router = APIRouter()


@router.get("/{lotto_type}", response_model=schemas.Prediction)
def get_prediction(
    lotto_type: schemas.LottoTypeEnum,
    draw_date: Optional[date] = Query(None, description="Specific draw date (must be a valid draw day)"),
    count: int = Query(1, ge=1, le=10, description="Number of combinations to generate"),
    db: Session = Depends(session.get_db)
):
    try:
        return prediction.generate_prediction(db, lotto_type, draw_date, count)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
