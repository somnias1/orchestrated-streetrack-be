# Phase 08 — Tests & verification (SPEC)

**Goal:** Pytest + Robot, coverage gate, §1.3 mapping table, DoD.

**Key TECHSPEC:** §1.3 (Success criteria & test mapping), §6 (Testing strategy), §8.3 (Definition of Done).

---

## Scope

1. **Unit tests**
   - **Auth:** Already present in `tests/unit/test_auth.py` (valid token → user_id; invalid/missing → 401). Keep and align with §1.3.
   - **Services:** Add unit tests for Category, Subcategory, Transaction, Hangout services: list/get/create/update/delete, user scoping, 404 when resource exists but not owned. Use DB session fixture (test DB or in-memory); no HTTP.

2. **Integration tests**
   - **Setup:** `tests/conftest.py` with overrides: `get_db` (session from test engine), `get_current_user_id` (inject user_id from header e.g. `X-Test-User-Id` so tests need no real JWT). TestClient via `httpx.ASGITransport`.
   - **Flows:** At least one full flow per resource (list, get, create, update, delete); 401 when no auth; 404 when accessing another user’s resource (by id). Optionally 422 on invalid body.

3. **Robot Framework**
   - **Smoke:** Root and health (status + structure).
   - **One flow per resource:** Categories, Subcategories, Transactions, Hangouts — create → list/get, status codes and response structure. Use BASE_URL (e.g. TestClient or live server); optional AUTH_TOKEN or test user header per §6.5.

4. **Coverage & gate**
   - Pytest coverage ≥ 80% (lines/statements) on `app/` per §6.2. Run `uv run pytest --cov`.
   - Gate: `uv run pytest && uv run robot tests/robot && uv run ruff check .` must pass before every commit.

5. **§1.3 mapping table**
   - Fill the table in TECHSPEC §1.3 with concrete tool and file/suite for each row. Commit in this phase (in TECHSPEC or in phase summary and reference in TECHSPEC).

6. **DoD (§8.3)**
   - Code matches this spec; all §1.3 cases covered; README documents how to run tests; gate passed; phase branch merged to main; `phase-08-SUMMARY.md` committed before merge.

---

## Out of scope (Phase 08)

- Changing application behavior or API contract.
- New endpoints or features.
- Coverage for branches/functions below 70% if gate is explicitly relaxed for this phase (otherwise meet §6.2).
