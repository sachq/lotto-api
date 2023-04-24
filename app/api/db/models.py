from sqlalchemy import Column, Integer, String, Date

from . import Base


class LottoDraw(Base):
    __tablename__ = "lotto_draw"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    A = Column(String, nullable=False)
    B = Column(String, nullable=False)
    C = Column(String, nullable=False)
    D = Column(String, nullable=False)
    E = Column(String, nullable=False)
    J = Column(String, nullable=False)
