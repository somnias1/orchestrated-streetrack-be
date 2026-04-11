# Project State

## Current Phase

Phase 20 — Transaction CSV export format (complete)

## Last Task Completed

Phase 20: `GET /transaction-manager/export` CSV uses `dd/mm/yyyy`, fixed `$` column, value, category_name, subcategory_name, description, hangout_name; nested joinedload for category; unit and integration tests; TECHSPEC/ROADMAP/STATE/SPEC/SUMMARY on branch merged to `main`.

## Next Task

Next backlog item or Phase 21 when defined on ROADMAP.

## Key Decisions

- Optional column/relationship annotations omitted in ORM where Mapped[Optional[...]] triggered SQLAlchemy + Python 3.14 typing path; runtime behavior unchanged.
- Initial migration hand-written so phase does not require local Postgres/psycopg2 to generate.
- **psycopg2-binary**: Pinned version caused `DLL load failed` for `_psycopg` on some setups (e.g. Windows). Relaxed to `>=2.9.10` so a compatible wheel can be used; `alembic upgrade head` and app run successfully. Documented in phase-02-SUMMARY.
- Finance expansion will use three separate Home endpoints (`/dashboard/balance`, `/dashboard/month-balance`, `/dashboard/due-periodic-expenses`) so heavier queries do not block lighter widgets in the frontend.
- Periodic expense due-status is month-based: a periodic subcategory is considered paid for a selected month if at least one transaction exists for that subcategory in that month.
- Import resolves existing category + subcategory pairs only and returns a normalized payload for strict bulk transaction creation.
- Phase 17: list `name` filter uses `ILIKE '%value%'`; `name` query omitted means no name filter.
- Phase 19: `GET /transactions/` uses the same `PaginatedRead` envelope as categories/subcategories/hangouts (`items`, `total`, `skip`, `limit`, `has_more`, `next_skip`).
- Phase 20: CSV export uses European date and fixed `$` column; category name from subcategory’s parent category.

## Blockers

None.
