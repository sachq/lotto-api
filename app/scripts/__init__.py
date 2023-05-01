from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from app.api.db.models import LottoDraw, LottoType

session_maker = sessionmaker(
    bind=create_engine('postgresql://sachq:$hinyHen89@localhost:5432/lotto'))

with session_maker() as session:
    lotto_type = session.query(LottoType).filter(
        LottoType.name == 'Megamillion').first()
    last_draw = session.query(LottoDraw).filter(
        LottoDraw.lotto_type_id == lotto_type.id).order_by(
        desc(LottoDraw.draw_date)).first()
    last_draw = session.query(LottoDraw).join(LottoType).filter(
        LottoType.name == 'Megamillion').order_by(
        desc(LottoDraw.draw_date)).first()
    print(last_draw.draw_date)
