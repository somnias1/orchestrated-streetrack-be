# Phase 01 — Foundation (SPEC)

**Scope:** Project scaffold, dependencies, tooling, app structure, `.gitattributes` per ROADMAP. Key TECHSPEC: §2.1, §2.2, §2.3, §3.2.

## Goals

1. **§2.1 Runtime & platform** — Python 3.14+ (pin in pyproject.toml), FastAPI, PostgreSQL via SQLAlchemy 2 + psycopg2, **uv** for package/deps, **Ruff** for lint/format.
2. **§2.2 Dependencies** — Exact versions in `pyproject.toml` (no `^` or `~`): fastapi[standard], sqlalchemy, alembic, pydantic-settings, python-jose[cryptography], requests, psycopg2-binary; dev: pytest, pytest-cov, httpx, robotframework, robotframework-requests.
3. **§2.3 Hard constraints** — `.gitattributes` with `* text=auto eol=lf`; no secrets in repo; exact dependency versions.
4. **§3.2 Project structure** — All app source under `app/`: `main.py`, `auth.py`, `db/` (base, config, session), `models/`, `schemas/`, `services/`, `routers/`; `tests/` with `unit/`, `integration/`, `robot/`. Root: pyproject.toml, uv.lock, .env.example.

## Deliverables

- `pyproject.toml` with Python 3.14+, [project], [project.optional-dependencies], exact pins, Ruff config (or [tool.ruff]).
- `uv.lock` generated.
- `.gitattributes` with `* text=auto eol=lf`.
- `app/main.py` — FastAPI app, CORS from settings, lifespan (engine create/dispose placeholder), include_router placeholders optional for later phases.
- `app/auth.py` — Stub or placeholder for get_current_user_id (Phase 03).
- `app/db/` — base.py (DeclarativeBase, get_engine, session_factory), config.py (Settings from env), session.py (get_db).
- `app/models/` — empty or `__init__.py` (models in Phase 02).
- `app/schemas/` — empty or `__init__.py`.
- `app/services/` — empty or `__init__.py`.
- `app/routers/` — empty or `__init__.py`.
- `tests/unit/`, `tests/integration/`, `tests/robot/` — minimal passing pytest and Robot so gate `uv run pytest && uv run robot tests/robot && uv run ruff check .` passes.
- `.env.example` with DATABASE_URL, AUTH0_*, CORS_ALLOWED_ORIGINS placeholders.

## Out of scope (later phases)

- Alembic migrations, ORM models (Phase 02).
- Auth0 JWT implementation (Phase 03).
- CRUD routers, services, schemas (Phases 04–07).

## Gate

Before every commit: `uv run pytest && uv run robot tests/robot && uv run ruff check .`
