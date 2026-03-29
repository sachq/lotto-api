from datetime import date
from enum import Enum

from pydantic import BaseModel


class LottoTypeEnum(str, Enum):
    powerball = "powerball"
    megamillion = "megamillion"


class LottoType(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


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
        from_attributes = True


class PaginatedDraws(BaseModel):
    items: list[LottoDraw]
    page: int
    per_page: int
    total_items: int
    total_pages: int


class Combination(BaseModel):
    numbers: list[int]
    bonus_number: int


class Prediction(BaseModel):
    lotto_type: str
    draw_date: date
    combinations: list[Combination]
