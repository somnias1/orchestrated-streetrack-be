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

Migrations are managed with **Alembic**. URL is taken from `DATABASE_URL` (via `app.db.config.Settings`); no URL in `alembic.ini`.

### Apply migrations

Ensure `DATABASE_URL` in `.env` points at your PostgreSQL database, then:

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

# Robot Framework (smoke / API)
uv run robot tests/robot

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

See `.env.example` for a template.

## Key decisions

- **Spec-first, phase-driven**: See `FRAMEWORK.md`, `TECHSPEC.md`, `.planning/phase-00-ROADMAP.md`.
- **Migrations**: Create with `alembic revision --autogenerate`; apply with `alembic upgrade head`.
- **Exact dependency versions** in `pyproject.toml` (no `^` or `~`).
