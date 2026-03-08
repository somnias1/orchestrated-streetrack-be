from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.db.config import Settings


def get_engine():
    settings = Settings()
    return create_engine(settings.database_url, pool_pre_ping=True)


def session_factory(engine=None):
    if engine is None:
        engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass
