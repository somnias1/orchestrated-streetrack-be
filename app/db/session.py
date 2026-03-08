from collections.abc import Generator

from fastapi import Request
from sqlalchemy.orm import Session

from app.db.base import session_factory


def get_db(request: Request) -> Generator[Session]:
    """Yield a request-scoped DB session. Engine is set in app lifespan."""
    engine = request.app.state.engine
    session_factory_instance = session_factory(engine)
    db = session_factory_instance()
    try:
        yield db
    finally:
        db.close()
