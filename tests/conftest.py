"""
Pytest fixtures for unit and integration tests.
§6.4: conftest for get_db override, auth override, TestClient.
Phase 16: tests use a dedicated Postgres test DB (TEST_DATABASE_URL); real DB is never touched.
Same migration files apply to both DBs; test DB is migrated at session start.
"""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from app.auth import get_current_user_id
from app.db.base import session_factory
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
    """Postgres URL for test DB; read from Settings (loads .env) so .env is the source of truth."""
    from app.db.config import Settings

    url = (Settings().test_database_url or "").strip()
    if not url or not url.lower().startswith("postgresql"):
        pytest.skip(
            "TEST_DATABASE_URL must be a Postgres URL (e.g. postgresql://.../streetrack_test). "
            "Same migrations apply to main and test DB."
        )
    return url


def _run_migrations_against(url: str) -> None:
    """Run Alembic migrations against the given URL (same files as main DB)."""
    from alembic import command
    from alembic.config import Config

    old = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = url
    try:
        cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
        command.upgrade(cfg, "head")
    finally:
        if old is not None:
            os.environ["DATABASE_URL"] = old
        else:
            os.environ.pop("DATABASE_URL", None)


@pytest.fixture(scope="session")
def test_engine():
    """Session-scoped Postgres test DB (TEST_DATABASE_URL). Migrations run at session start."""
    url = _test_database_url()
    _run_migrations_against(url)
    engine = create_engine(url, pool_pre_ping=True)
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
    app.dependency_overrides.pop(get_current_user_id, None)
