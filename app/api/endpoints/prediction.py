from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.db import schemas, session
from app.api.services import prediction

router = APIRouter()


@router.get("/{lotto_type}", response_model=schemas.Prediction)
def get_prediction(
    lotto_type: schemas.LottoTypeEnum,
    db: Session = Depends(session.get_db)
):
    return prediction.generate_prediction(db, lotto_type)
