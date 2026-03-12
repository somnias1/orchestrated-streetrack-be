# Phase 16 — Finance expansion tests & handoff

## Goal (from ROADMAP)

Add tests, robot coverage where practical, and FE contract verification for the new finance APIs. Use a **dedicated test database** so the test suite never touches or drops tables in the real database.

## Scope

### 1. Test database (dedicated DB, no real DB)

- **Requirement**: Pytest (unit + integration) must use a **separate database** for all tests. The real application database must never be used or modified by the test suite.
- **Implementation**:
  - Prefer **SQLite** for tests when possible (e.g. in-memory `sqlite:///:memory:`) so no extra Postgres is required for running tests.
  - Support optional **TEST_DATABASE_URL** (e.g. Postgres) for environments that prefer a dedicated Postgres test DB.
  - In `conftest.py`: create a test-only engine (from `TEST_DATABASE_URL` or default SQLite); create tables via `Base.metadata.create_all`; override `get_db` (and any session/engine usage) so that unit and integration tests use this engine only. Remove any use of production `get_engine()` / `DATABASE_URL` in test paths.
  - Ensure no test code deletes or truncates tables in the production database; all cleanup is confined to the test engine/session.
- **TECHSPEC**: §6 (testing), §8.3 (DoD).

### 2. Finance expansion test coverage (§1.3)

- **Import/export**: Fill in the §1.3 row "Import/export: import preview vs existing pairs; export date-filtered CSV" with concrete pytest locations (unit + integration already added in Phase 15; verify and document).
- **All §1.3 cases** that apply to phases 11–15 remain covered; produce/update the **§1.3 mapping table** in TECHSPEC §1.3 so each case has a clear test file/suite reference.
- **TECHSPEC**: §1.3, §6.

### 3. Robot coverage (where practical)

- Add or extend Robot tests in `tests/robot/` to cover the **new finance-related APIs** where practical: dashboard (balance, month-balance, due-periodic-expenses), transaction manager (import preview, export), and/or filtering/bulk where feasible without heavy setup. Scope to what is practical (e.g. smoke-style checks, one flow per new area).
- **TECHSPEC**: §6 (acceptance/API tests).

### 4. FE contract verification

- Verify that the **API contract** (request/response shapes) for the finance expansion endpoints matches the TECHSPEC §4.3 and Pydantic schemas. At minimum: ensure OpenAPI (`/openapi.json`) exposes the documented endpoints and schemas (dashboard, transaction-manager, filters, bulk). Optionally add a small pytest that fetches `/openapi.json` and asserts presence and basic shape of key paths/schemas.
- **TECHSPEC**: §1.3 (API contract), §4.3.

### 5. DoD and handoff

- Gate passes before every commit: `uv run pytest && uv run robot tests/robot && uv run ruff check .`.
- §1.3 mapping table updated; phase SUMMARY and STATE.md updated; branch merged to main with `--no-ff`.
- **TECHSPEC**: §8.3.

## Out of scope

- Changing production database URL or migration behavior.
- Adding new application features beyond tests and verification.

## Success criteria

1. All pytest (unit + integration) use only the test database (SQLite or TEST_DATABASE_URL); production DB is never touched.
2. §1.3 mapping table includes import/export and any other finance cases; all applicable cases have a test location.
3. Robot suite includes coverage for new finance APIs where practical.
4. FE contract verification confirms finance endpoints and schemas in OpenAPI/spec.
5. Gate passes; phase SUMMARY committed; STATE.md updated; merge to main complete.
