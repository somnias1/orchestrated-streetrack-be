# Phase 02 — Data model + migrations

## What was built

- **ORM models** (TECHSPEC §4.1): `Category`, `Subcategory`, `Transaction`, `Hangout` in `app/models/` with UUID PKs, `user_id`, FKs (CASCADE/SET NULL), and relationships. Optional columns left unannotated / no `Mapped[Optional[...]]` to avoid SQLAlchemy typing issues with Python 3.14.
- **Alembic** (§4.2): `alembic.ini`, `alembic/env.py` using `app.db.config.Settings().database_url` and `Base.metadata`; all models imported in env so metadata is complete.
- **Initial migration**: Single revision creating `categories`, `hangouts`, `subcategories`, `transactions` with correct columns and foreign keys (hand-written; autogenerate was not run due to local psycopg2/DLL environment).

## Files changed

- `.planning/phase-02-SPEC.md`: Phase scope and tasks.
- `app/models/category.py`, `hangout.py`, `subcategory.py`, `transaction.py`: New ORM models; `__future__` annotations; TYPE_CHECKING imports for forward refs.
- `app/models/__init__.py`: Re-exports for Category, Hangout, Subcategory, Transaction.
- `alembic.ini`: Commented-out url; URL supplied from Settings in env.py.
- `alembic/env.py`: get_url() from Settings; target_metadata = Base.metadata; model imports for autogenerate.
- `alembic/versions/837ee5832ce5_*.py`: Initial upgrade/downgrade for four tables.

## Decisions made

- **Optional / Union annotations**: Under Python 3.14, SQLAlchemy’s `de_stringify_union_elements` / `make_union_type` path raises when resolving `Mapped[Optional[str]]` (and similar). We avoided that by not annotating optional columns and the optional `hangout` relationship with `Mapped[...]`; columns and relationship still work at runtime.
- **Initial migration**: Written by hand so the phase does not depend on a working PostgreSQL connection or psycopg2 DLL on the host; `uv run alembic upgrade head` remains the way to apply it where DB is available.

## Tests added

- None this phase (no new pytest or Robot tests; existing gate still passes).

## Known issues / follow-ups

- None. When Postgres and psycopg2 are available, run `uv run alembic upgrade head` to create tables. Pydantic schemas and CRUD are Phase 04+.
