from datetime import date

from pydantic import BaseModel


class LottoType(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class LottoDraw(BaseModel):
    id: int
    draw_date: date
    A: str
    B: str
    C: str
    D: str
    E: str
    J: str
    lotto_type: LottoType

    class Config:
        orm_mode = True
