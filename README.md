# Streetrack Backend

FastAPI, PostgreSQL, Auth0. REST API for expense tracking (categories, subcategories, transactions, hangouts).

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) for dependencies
- PostgreSQL (for running the app and migrations)

## Setup

```bash
# Install dependencies (exact versions, no ^ or ~)
uv sync

# Copy env and set DATABASE_URL and optional Auth0/CORS
cp .env.example .env
# Edit .env with your DATABASE_URL (required for app and migrations)
```

## Run (dev)

```bash
uv run uvicorn app.main:app --reload
```

- Root: `GET /`
- Health: `GET /health`
- OpenAPI: `GET /openapi.json`

## Migrations

Migrations are managed with **Alembic**. The same migration files apply to **both** the main DB and the test DB; you choose which database is migrated by which URL is in the environment when you run the command.

- **Main DB:** set `DATABASE_URL` in `.env` to your main PostgreSQL, then run `uv run alembic upgrade head`. That applies all migrations to the main DB.
- **Test DB:** set `TEST_DATABASE_URL` in `.env` to a separate Postgres DB (e.g. `streetrack_test`). When you run pytest, the test harness runs `alembic upgrade head` against that URL at session start, so the test DB is kept in sync. You can also apply migrations to the test DB manually with `DATABASE_URL=$TEST_DATABASE_URL uv run alembic upgrade head` (or the Windows equivalent).

### Apply migrations (main DB)

Ensure `DATABASE_URL` in `.env` points at your main PostgreSQL database, then:

```bash
uv run alembic upgrade head
```

### Create migrations (autogenerate)

After changing ORM models in `app/models/`, generate a new revision by comparing the database to `Base.metadata`:

```bash
uv run alembic revision --autogenerate -m "short description of the change"
```

- Requires a running PostgreSQL and a valid `DATABASE_URL`.
- Review the generated script in `alembic/versions/` and edit if needed (e.g. renames, data backfills), then run `uv run alembic upgrade head` to apply.

### Other Alembic commands

```bash
# Current revision
uv run alembic current

# History
uv run alembic history -v

# Downgrade one revision
uv run alembic downgrade -1
```

## Tests and lint

```bash
# Unit + integration (pytest)
uv run pytest

# With coverage
uv run pytest --cov

# Robot Framework (smoke / API; requires API running at BASE_URL, default http://localhost:8000)
uv run robot tests/robot
# Optional: set AUTH_TOKEN for protected flow tests (Bearer JWT from Auth0).

# Lint and format (Ruff)
uv run ruff check .
uv run ruff format .
```

**Gate (before every commit):**

```bash
uv run pytest && uv run robot tests/robot && uv run ruff check .
```

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes (for app and migrations) | PostgreSQL URL, e.g. `postgresql://user:pass@localhost:5432/streetrack` |
| `AUTH0_DOMAIN` | No | Auth0 tenant (JWT validation) |
| `AUTH0_AUDIENCE` | No | API audience |
| `AUTH0_ISSUER` | No | Token issuer |
| `CORS_ALLOWED_ORIGINS` | No | Comma-separated origins (default `http://localhost:3000`) |
| `TEST_DATABASE_URL` | Yes (for pytest) | Dedicated PostgreSQL DB for tests (e.g. `postgresql://user:pass@localhost:5432/streetrack_test`). Same migrations apply; test DB is migrated at pytest session start. |

See `.env.example` for a template. **Tests** require a separate Postgres test DB; they never use `DATABASE_URL`. Create the test DB (e.g. `streetrack_test`) and set `TEST_DATABASE_URL`; pytest will run migrations against it when the session starts.

## Key decisions

- **Spec-first, phase-driven**: See `FRAMEWORK.md`, `TECHSPEC.md`, `.planning/phase-00-ROADMAP.md`.
- **Migrations**: Create with `alembic revision --autogenerate`; apply with `alembic upgrade head`.
- **Exact dependency versions** in `pyproject.toml` (no `^` or `~`).
