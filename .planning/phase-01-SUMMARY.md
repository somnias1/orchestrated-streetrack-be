# Phase 01 — Foundation (SUMMARY)

## What was built

- **Dependencies and tooling:** `pyproject.toml` with Python 3.14+, exact pins (FastAPI, SQLAlchemy, Alembic, pydantic-settings, python-jose, requests, psycopg2-binary; dev: pytest, pytest-cov, httpx, robotframework, robotframework-requests, ruff). `uv.lock` generated.
- **Line endings:** `.gitattributes` with `* text=auto eol=lf` per TECHSPEC §2.3.
- **Config:** `.env.example` with DATABASE_URL, AUTH0_*, CORS_ALLOWED_ORIGINS. `app/db/config.py` Settings (pydantic-settings).
- **App scaffold:** `app/main.py` (FastAPI, CORS from settings, lifespan create/dispose engine), `app/auth.py` (stub for Phase 03), `app/db/` (base, config, session with get_db using app.state.engine), empty `app/models/`, `app/schemas/`, `app/services/`, `app/routers/`.
- **Tests:** `tests/unit/test_placeholder.py`, `tests/integration/test_health.py` (root + health via TestClient), `tests/robot/smoke.robot` (placeholder so gate passes without a running server).
- **GSD alignment:** `.cursor/gsd/` subagents and `.cursor/rules/gsd-git-workflow.mdc` updated to Python/FastAPI wording: gate `uv run pytest && uv run robot tests/robot && uv run ruff check .`.

## Files changed

- `.planning/phase-01-SPEC.md` — Phase 01 spec (committed on main before branch).
- `.cursor/gsd/subagents/phase.md`, `bootstrap.md`, `audit.md`, `README.md` — gate and tooling wording (uv, ruff, pytest, robot).
- `.cursor/rules/gsd-git-workflow.mdc` — gate command and checklist (uv/ruff/pytest/robot).
- `pyproject.toml` — project and deps, Ruff config, pytest/coverage options.
- `uv.lock` — lockfile.
- `.gitattributes`, `.env.example`, `.gitignore` — line endings, env template, ignore Robot outputs and .venv.
- `app/**` — main, auth stub, db (base, config, session), empty packages for models/schemas/services/routers.
- `tests/**` — unit placeholder, integration health, robot smoke placeholder.

## Decisions made

- **Ruff target-version:** Set to `py313` because Ruff 0.8.x does not support `py314` yet; project still requires Python 3.14+ in `requires-python`.
- **Robot in gate:** Phase 01 uses a trivial Robot test so the gate passes without starting a server; real API Robot tests in Phase 08.
- **get_db:** Request-scoped session; engine created in lifespan and stored on `app.state.engine`; `get_db` reads it from `Request`.

## Tests added

- `tests/unit/test_placeholder.py` — single pass for gate.
- `tests/integration/test_health.py` — GET `/` and GET `/health` via TestClient.
- `tests/robot/smoke.robot` — one placeholder test.

## Known issues / follow-ups

- None. Phase 02 will add Alembic and ORM models; Phase 03 will implement Auth0 in `app/auth.py`.
