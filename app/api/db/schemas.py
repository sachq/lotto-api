from datetime import date

from pydantic import BaseModel


class User(BaseModel):
    id: int
    date: date
    A: str
    B: str
    C: str
    D: str
    E: str
    J: str

    class Config:
        orm_mode = True
