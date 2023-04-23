from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from datetime import date

from app.api.db import crud, models, schemas, SessionLocal, engine
from app.api.db import session

router = APIRouter()


@router.get("/yearly")
async def yearly_summary():
    return {
        "data": {
            "name": "Yearly Summary",
            "date": date.today(),
        }
    }


@router.get("/users", response_model=list[schemas.User])
def get_users(db: Session = Depends(session.get_db)):
    users = crud.get_users(db)
    return users


@router.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(session.get_db)):
    user = crud.get_user(db, user_id)
    return user
