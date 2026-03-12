"""
Pytest fixtures for unit and integration tests.
§6.4: conftest for get_db override, auth override, TestClient.
Phase 16: tests use a dedicated test DB (SQLite or TEST_DATABASE_URL); real DB is never touched.
"""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from app.auth import get_current_user_id
from app.db.base import Base, session_factory
from app.db.session import get_db
from app.main import app
from app.models.category import Category
from app.models.hangout import Hangout
from app.models.subcategory import Subcategory
from app.models.transaction import Transaction
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete


def _test_database_url() -> str:
    """URL for test database: TEST_DATABASE_URL or in-memory SQLite (no real DB)."""
    explicit = os.environ.get("TEST_DATABASE_URL")
    if explicit:
        return explicit
    return "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine():
    """Session-scoped test DB (TEST_DATABASE_URL or SQLite); never production."""
    url = _test_database_url()
    opts = {}
    if url.startswith("sqlite"):
        opts["connect_args"] = {"check_same_thread": False}
    engine = create_engine(
        url,
        pool_pre_ping=not url.startswith("sqlite"),
        **opts,
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def _override_get_db_for_tests(test_engine):
    """Override get_db so all tests use the test engine; real DB is never used."""
    def get_db_override(request: Request) -> Generator:
        session_factory_instance = session_factory(test_engine)
        session = session_factory_instance()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = get_db_override
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def db_session(test_engine) -> Generator:
    """DB session for unit tests; tables cleaned at start, session closed at end (test DB only)."""
    session_factory_instance = session_factory(test_engine)
    session = session_factory_instance()
    session.execute(delete(Transaction))
    session.execute(delete(Hangout))
    session.execute(delete(Subcategory))
    session.execute(delete(Category))
    session.commit()
    yield session
    session.close()


@pytest.fixture
def clean_db(test_engine) -> Generator:
    """Clear CRUD tables before test (integration tests; test DB only)."""
    session_factory_instance = session_factory(test_engine)
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
def client(clean_db: None) -> Generator[TestClient]:
    """TestClient with auth overridden; clean_db runs first for tests that need it."""
    app.dependency_overrides[get_current_user_id] = _override_get_current_user_id
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
