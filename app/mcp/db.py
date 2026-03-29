from contextlib import contextmanager

from app.api.db import SessionLocal


@contextmanager
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
