# Project State

## Current Phase

Phase 11 — Filtering and sorting foundation (complete)

## Last Task Completed

Phase 11: List filters for categories (is_income), subcategories (belongs_to_income, category_id), and transactions (year/month/day, subcategory_id, hangout_id); newest-first sort; §1.3 tests and mapping.

## Next Task

Phase 12: Periodic expenses — subcategory periodic-expense fields, validation, and due-status business rules.

## Key Decisions

- Optional column/relationship annotations omitted in ORM where Mapped[Optional[...]] triggered SQLAlchemy + Python 3.14 typing path; runtime behavior unchanged.
- Initial migration hand-written so phase does not require local Postgres/psycopg2 to generate.
- **psycopg2-binary**: Pinned version caused `DLL load failed` for `_psycopg` on some setups (e.g. Windows). Relaxed to `>=2.9.10` so a compatible wheel can be used; `alembic upgrade head` and app run successfully. Documented in phase-02-SUMMARY.
- Finance expansion will use three separate Home endpoints (`/dashboard/balance`, `/dashboard/month-balance`, `/dashboard/due-periodic-expenses`) so heavier queries do not block lighter widgets in the frontend.
- Periodic expense due-status is month-based: a periodic subcategory is considered paid for a selected month if at least one transaction exists for that subcategory in that month.
- Import resolves existing category + subcategory pairs only and returns a normalized payload for strict bulk transaction creation.

## Blockers

None.
