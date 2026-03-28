import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from . import Base


class BaseModel(Base):
    __abstract__ = True
    created_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow,
                           server_default=sa.text('CURRENT_TIMESTAMP'))
    updated_at = sa.Column(sa.DateTime, onupdate=datetime.datetime.utcnow,
                           server_onupdate=sa.text('CURRENT_TIMESTAMP'))
    is_active = sa.Column(sa.Boolean, nullable=False, default=True,
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
    __table_args__ = (
        sa.Index('ix_winning_draw_date_lotto_type', 'draw_date', 'lotto_type_id'),
        sa.UniqueConstraint('draw_date', 'lotto_type_id', name='uq_draw_date_lotto_type'),
    )

    id = sa.Column(sa.Integer, primary_key=True)
    draw_date = sa.Column(sa.Date, nullable=False, index=True)
    A = sa.Column(sa.SmallInteger, nullable=False, index=True)
    B = sa.Column(sa.SmallInteger, nullable=False, index=True)
    C = sa.Column(sa.SmallInteger, nullable=False, index=True)
    D = sa.Column(sa.SmallInteger, nullable=False, index=True)
    E = sa.Column(sa.SmallInteger, nullable=False, index=True)
    J = sa.Column(sa.SmallInteger, nullable=False, index=True)
    lotto_type_id = sa.Column(sa.Integer, sa.ForeignKey("lotto_type.id"),
                              nullable=False, index=True)
    lotto_type = relationship("LottoType", back_populates="winning_draws")
