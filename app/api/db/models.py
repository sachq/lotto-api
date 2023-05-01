import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from . import Base


class BaseModel(Base):
    __abstract__ = True
    created_at = sa.Column(sa.DateTime, default=datetime.date.today,
                           server_default=sa.text('CURRENT_TIMESTAMP'))
    updated_at = sa.Column(sa.DateTime,
                           server_onupdate=sa.text('CURRENT_TIMESTAMP'))
    is_active = sa.Column(sa.Boolean, nullable=False,
                          server_default=sa.text('true'))


class LottoType(BaseModel):
    __tablename__ = "lotto_type"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, unique=True, nullable=False, index=True)
    winning_draws = relationship("LottoDraw", back_populates="lotto_type")

    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "winning_draws": [draw.dict() for draw in self.winning_draws],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": self.is_active,
        }


class LottoDraw(BaseModel):
    __tablename__ = "winning_draw"

    id = sa.Column(sa.Integer, primary_key=True)
    draw_date = sa.Column(sa.Date, nullable=False, index=True)
    A = sa.Column(sa.SmallInteger, nullable=False, index=True)
    B = sa.Column(sa.SmallInteger, nullable=False, index=True)
    C = sa.Column(sa.SmallInteger, nullable=False, index=True)
    D = sa.Column(sa.SmallInteger, nullable=False, index=True)
    E = sa.Column(sa.SmallInteger, nullable=False, index=True)
    J = sa.Column(sa.SmallInteger, nullable=False, index=True)
    lotto_type_id = sa.Column(sa.Integer, sa.ForeignKey("lotto_type.id"),
                              nullable=False)
    lotto_type = relationship("LottoType", back_populates="winning_draws")

    def dict(self):
        return {
            "id": self.id,
            "draw_date": self.draw_date,
            "A": self.A,
            "B": self.B,
            "C": self.C,
            "D": self.D,
            "E": self.E,
            "J": self.J,
            "lotto_type_id": self.lotto_type_id,
            "lotto_type": self.lotto_type.dict(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": self.is_active,
        }
