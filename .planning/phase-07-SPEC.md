# Phase 07 — Hangouts CRUD (Spec)

**Phase:** 07  
**Name:** Hangouts CRUD  
**Goal:** CRUD scoped by `user_id`.  
**Key TECHSPEC:** §4.1, §4.3.

## Scope

- **Schemas** (§4.1): `HangoutRead`, `HangoutCreate`, `HangoutUpdate` — fields per TECHSPEC (id, name, description, date, user_id for Read; name required, date required, description optional for Create; all optional for Update).
- **Service** (§3.2, §4.1): `HangoutService` (or module `app.services.hangout`) — `list_hangouts`, `get_hangout`, `create_hangout`, `update_hangout`, `delete_hangout`; all scoped by `user_id`; 404 when resource not found or not owned.
- **Router** (§4.3): `app.routers.hangout` — GET/POST `/hangouts/`, GET/PATCH/DELETE `/hangouts/{hangout_id}`; query params `skip`, `limit` (defaults 0, 50) on list; `Depends(get_db)`, `CurrentUserId`.
- **App**: Include hangouts router in `app/main.py`.

## Out of scope

- No model or migration changes (Hangout ORM exists from Phase 02).
- No changes to Transactions or other resources.

## Definition of done (this phase)

- All Hangouts endpoints implemented and user-scoped.
- Gate `uv run pytest && uv run robot tests/robot && uv run ruff check .` passes.
- phase-07-SUMMARY.md written; STATE.md updated; branch merged to main with `--no-ff`.
