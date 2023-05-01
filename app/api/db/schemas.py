from datetime import date

from pydantic import BaseModel


class LottoDraw(BaseModel):
    id: int
    draw_date: date
    A: str
    B: str
    C: str
    D: str
    E: str
    J: str
    lotto_type_id: int

    class Config:
        orm_mode = True
