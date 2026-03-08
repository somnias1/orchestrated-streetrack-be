# Project State

## Current Phase

Phase 08 — Tests & verification (complete)

## Last Task Completed

Phase 08: Pytest unit (auth, category, subcategory, transaction, hangout services) and integration (one flow per resource, 401, 404, 422); Robot smoke + categories/hangouts flow; conftest (get_db/auth overrides); §1.3 mapping table in TECHSPEC; coverage ≥80%; phase branch merged to main.

## Next Task

Phase 09+ (new features per BACKLOG / FRAMEWORK.md §6).

## Key Decisions

- Optional column/relationship annotations omitted in ORM where Mapped[Optional[...]] triggered SQLAlchemy + Python 3.14 typing path; runtime behavior unchanged.
- Initial migration hand-written so phase does not require local Postgres/psycopg2 to generate.
- **psycopg2-binary**: Pinned version caused `DLL load failed` for `_psycopg` on some setups (e.g. Windows). Relaxed to `>=2.9.10` so a compatible wheel can be used; `alembic upgrade head` and app run successfully. Documented in phase-02-SUMMARY.

## Blockers

None.
