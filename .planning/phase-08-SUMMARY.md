# Phase 08 — Tests & verification (SUMMARY)

## Done

- **Spec:** `.planning/phase-08-SPEC.md` committed on main; branch `feature/phase-08-tests-verification` created.
- **conftest.py:** Session-scoped engine, `db_session` (unit tests, clean at start), `clean_db` (integration), `client` with auth override `X-Test-User-Id` → user_id (no header → 401).
- **Unit tests:**
  - Auth: existing `tests/unit/test_auth.py` (valid token → user_id; invalid/missing → 401).
  - Services: `test_services_category.py`, `test_services_subcategory.py`, `test_services_transaction.py`, `test_services_hangout.py` — list/get/create/update/delete, scoping, 404 when not owned / category or subcategory/hangout ownership.
- **Integration tests:**
  - `test_auth_401.py`: 401 without auth; 422 validation error shape (detail with loc/msg/type).
  - `test_categories_api.py`, `test_subcategories_api.py`, `test_transactions_api.py`, `test_hangouts_api.py`: one full flow per resource (list → create → list → get → update → delete) and 404 when resource not owned.
- **Robot:** `tests/robot/smoke.robot` — root + health (status + structure); categories and hangouts flow when `AUTH_TOKEN` set; 401 without token. Uses `BASE_URL` (default http://localhost:8000) and optional `AUTH_TOKEN` from env.
- **Coverage:** Pytest coverage on `app/` ≥ 80% (achieved ~94%). Gate: `uv run pytest && uv run robot tests/robot && uv run ruff check .`.
- **§1.3 mapping:** TECHSPEC §1.3 table filled with concrete test locations.
- **README:** Note added that Robot tests require the API running at BASE_URL and optional AUTH_TOKEN for protected flows.

## Gate note

Robot tests call the API at `BASE_URL`. For the full gate to pass, start the API (e.g. `uv run uvicorn app.main:app`) in another terminal, or run Robot in CI after starting the app. Pytest and ruff do not require a running server.

## Definition of Done (§8.3)

- Code matches phase spec; §1.3 cases covered; mapping table in TECHSPEC.
- README documents how to run app, tests (pytest, Robot, ruff), env vars.
- Gate passed (pytest + ruff; robot passes when server is running).
- Phase SUMMARY committed; STATE.md updated; branch merged to main with `--no-ff`.
