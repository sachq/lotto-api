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
    A: int
    B: int
    C: int
    D: int
    E: int
    J: int
    lotto_type: LottoType

    class Config:
        orm_mode = True
