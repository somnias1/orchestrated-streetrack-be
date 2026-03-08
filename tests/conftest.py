"""
Pytest fixtures for unit and integration tests.
§6.4: conftest for get_db override, auth override, TestClient.
"""

from __future__ import annotations

from collections.abc import Generator

import pytest
from app.auth import get_current_user_id
from app.db.base import get_engine, session_factory
from app.main import app
from app.models.category import Category
from app.models.hangout import Hangout
from app.models.subcategory import Subcategory
from app.models.transaction import Transaction
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import delete


@pytest.fixture(scope="session")
def engine():
    """Session-scoped engine (uses DATABASE_URL)."""
    return get_engine()


@pytest.fixture
def db_session(engine) -> Generator:
    """DB session for unit tests; tables cleaned at start, session closed at end."""
    session_factory_instance = session_factory(engine)
    session = session_factory_instance()
    # Clean state so each test starts with empty tables
    session.execute(delete(Transaction))
    session.execute(delete(Hangout))
    session.execute(delete(Subcategory))
    session.execute(delete(Category))
    session.commit()
    yield session
    session.close()


@pytest.fixture
def clean_db(engine) -> Generator:
    """Truncate CRUD tables before test (for integration tests that need clean state)."""
    session_factory_instance = session_factory(engine)
    session = session_factory_instance()
    session.execute(delete(Transaction))
    session.execute(delete(Hangout))
    session.execute(delete(Subcategory))
    session.execute(delete(Category))
    session.commit()
    session.close()
    yield


def _override_get_current_user_id(request: Request) -> str:
    """Return X-Test-User-Id header or raise 401 (for integration tests without real JWT)."""
    user_id = request.headers.get("X-Test-User-Id")
    if not user_id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


@pytest.fixture
def client() -> Generator[TestClient]:
    """TestClient with auth overridden: X-Test-User-Id header → user_id; no header → 401."""
    app.dependency_overrides[get_current_user_id] = _override_get_current_user_id
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
