# Project State

## Current Phase

Phase 04 — Categories CRUD (complete)

## Last Task Completed

Phase 04: Categories CRUD — router, service, schemas (CategoryRead/Create/Update); list/get/create/update/delete scoped by user_id; 404 when not owned; gate passed; branch merged to main.

## Next Task

Phase 05 — Subcategories CRUD: CRUD + category ownership checks. Create branch feature/phase-05-subcategories-crud, write phase-05-SPEC.md, implement per §4.1, §4.3.

## Key Decisions

- Optional column/relationship annotations omitted in ORM where Mapped[Optional[...]] triggered SQLAlchemy + Python 3.14 typing path; runtime behavior unchanged.
- Initial migration hand-written so phase does not require local Postgres/psycopg2 to generate.
- **psycopg2-binary**: Pinned version caused `DLL load failed` for `_psycopg` on some setups (e.g. Windows). Relaxed to `>=2.9.10` so a compatible wheel can be used; `alembic upgrade head` and app run successfully. Documented in phase-02-SUMMARY.

## Blockers

None.
