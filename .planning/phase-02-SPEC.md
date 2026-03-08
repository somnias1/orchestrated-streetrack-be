# Phase 02 — Data model + migrations

**Goal (ROADMAP):** ORM models (Category, Subcategory, Transaction, Hangout), Alembic, initial migration.

**Key TECHSPEC:** §4.1 (Data model — ORM), §4.2 (Storage — Alembic).

---

## Scope

### 1. ORM models (§4.1)

All in `app/models/`; UUID primary keys; `user_id` (str, nullable) on all four. Use `app.db.base.Base` as declarative base.

| Model | Table | Columns | Relationships |
|-------|--------|---------|----------------|
| **Category** | `categories` | id (UUID PK), user_id (str, nullable), name, description (str, nullable, 1024), is_income (bool) | One-to-many → Subcategory |
| **Subcategory** | `subcategories` | id (UUID PK), category_id (FK → categories.id ON DELETE CASCADE), user_id (str, nullable), name, description (str, nullable, 1024), belongs_to_income (bool) | Many-to-one Category; one-to-many Transaction |
| **Transaction** | `transactions` | id (UUID PK), subcategory_id (FK → subcategories.id ON DELETE CASCADE), value (int), description (str), date (date), hangout_id (FK → hangouts.id ON DELETE SET NULL, nullable), user_id (str, nullable) | Many-to-one Subcategory; many-to-one Hangout (optional) |
| **Hangout** | `hangouts` | id (UUID PK), name, description (str, nullable, 1024), date (date), user_id (str, nullable) | One-to-many Transaction |

- Export all four from `app.models` (or per-model modules and re-export in `__init__.py`).

### 2. Alembic (§4.2)

- Initialize Alembic at repo root: `alembic.ini`, `alembic/` with env.py and script.py.mako.
- Configure `alembic.ini` and `alembic/env.py` to use `app.db.base.Base.metadata` and `app.db.config.Settings().database_url` (no hardcoded URLs).
- **Initial migration:** one revision that creates tables `categories`, `subcategories`, `transactions`, `hangouts` with the columns and FKs above.
- **Creating future migrations:** use **autogenerate**. After changing ORM models, run `uv run alembic revision --autogenerate -m "description"` (requires `DATABASE_URL` and a running DB). Review the generated script in `alembic/versions/`, then apply with `uv run alembic upgrade head`. See README.

### 3. Out of scope this phase

- Pydantic schemas (Create/Update/Read) — Phase 04+.
- Routers, services, auth wiring — later phases.
- No API changes; app may still start with empty or stub routers.

---

## Tasks (atomic commits)

1. **feat(02): add phase-02 spec** — this spec committed on the phase branch.
2. **feat(02): add ORM models Category, Subcategory, Transaction, Hangout** — implement in `app/models/`, wire to Base.
3. **chore(02): add Alembic and initial migration** — alembic init, config from app.db, first migration creating all four tables. New migrations thereafter: create via `alembic revision --autogenerate`, apply via `alembic upgrade head`.

---

## Definition of Done (Phase 02)

- [ ] Spec committed before implementation code.
- [ ] All four ORM models match §4.1 (columns, types, FKs, relationships).
- [ ] Alembic runs: `uv run alembic upgrade head` creates the four tables in PostgreSQL.
- [ ] Gate passes: `uv run pytest && uv run robot tests/robot && uv run ruff check .`
