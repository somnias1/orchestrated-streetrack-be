# Project State

## Current Phase

Phase 03 — Auth (complete)

## Last Task Completed

Phase 03: Auth0 JWT validation, get_current_user_id, CurrentUserId. Spec committed; branch feature/phase-03-auth; app/auth.py implemented; unit tests for valid/invalid/missing token; gate passed.

## Next Task

Phase 04 — Categories CRUD: Router, service, schemas, list/get/create/update/delete. Create branch feature/phase-04-categories-crud, write phase-04-SPEC.md, implement per §3.2, §4.1, §4.3.

## Key Decisions

- Optional column/relationship annotations omitted in ORM where Mapped[Optional[...]] triggered SQLAlchemy + Python 3.14 typing path; runtime behavior unchanged.
- Initial migration hand-written so phase does not require local Postgres/psycopg2 to generate.
- **psycopg2-binary**: Pinned version caused `DLL load failed` for `_psycopg` on some setups (e.g. Windows). Relaxed to `>=2.9.10` so a compatible wheel can be used; `alembic upgrade head` and app run successfully. Documented in phase-02-SUMMARY.

## Blockers

None.
