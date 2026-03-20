# TECHSPEC audit

**Date:** 2026-03-19  
**Reference:** `TECHSPEC.md` (as of repo HEAD)  
**Method:** Static review of tests, README, `.planning/` artifacts, `app/`; `uv run pytest --cov` and `pytest --cov --cov-branch`; `uv run ruff check .`; `git branch -a`.

---

## 1. §1.3 success criteria → test coverage mapping

Each row is a §1.3 **observable** criterion. **Covered** means at least one automated test (pytest or Robot) clearly targets that behavior; locations are verified to exist in the tree at audit time.

| §1.3 case | Covered | Primary test locations (files / named tests) |
|-----------|---------|-----------------------------------------------|
| **Auth:** valid token → `user_id` | Yes | `tests/unit/test_auth.py::test_valid_token_returns_user_id` |
| **Auth:** invalid token → 401 | Yes | `tests/unit/test_auth.py::test_invalid_token_raises_401` |
| **Auth:** missing token → 401 | Yes | `tests/unit/test_auth.py::test_missing_token_raises_401`; `tests/integration/test_auth_401.py` (list/post categories without auth); Robot `tests/robot/smoke.robot` — *Protected endpoint without token returns 401* |
| **Categories:** list/get/create/update/delete scoped by `user_id` | Yes | `tests/unit/test_services_category.py` (list scoped, get/create/update/delete); `tests/integration/test_categories_api.py::test_categories_flow` |
| **Categories:** 404 when not owned | Yes | `tests/unit/test_services_category.py` (`test_get_category_404_when_not_owned`, update/delete not owned); `tests/integration/test_categories_api.py::test_categories_get_404_when_not_owned` |
| **Subcategories:** CRUD + category ownership | Yes | `tests/unit/test_services_subcategory.py`; `tests/integration/test_subcategories_api.py` |
| **Transactions:** CRUD + subcategory/hangout ownership | Yes | `tests/unit/test_services_transaction.py`; `tests/integration/test_transactions_api.py` |
| **Hangouts:** CRUD scoped; 404 when not owned | Yes | `tests/unit/test_services_hangout.py`; `tests/integration/test_hangouts_api.py` |
| **API contract:** 422 validation `detail: ValidationError[]` | Yes | `tests/integration/test_auth_401.py::test_validation_error_returns_422_detail` |
| **API contract:** responses match Pydantic / JSON shape | Yes (implicit) | Integration flows assert response keys and status codes; `tests/integration/test_openapi_contract.py::test_openapi_exposes_finance_endpoints` for FE contract surface |
| **Smoke + one flow per resource (Robot)** | Yes | `tests/robot/smoke.robot` — root, health, 401, and per-resource flows when `AUTH_TOKEN` set (categories, hangouts, subcategories, transactions); plus dashboard balance and transaction-manager export |
| **Categories / subcategories filters** (type; `category_id` on subcategories) | Yes | `tests/unit/test_services_category.py::test_list_categories_filter_by_is_income`; `tests/unit/test_services_subcategory.py::test_list_subcategories_filter_by_belongs_to_income`, `test_list_subcategories_filter_by_category_id` |
| **Transactions filters** (date tree, `subcategory_id`, `hangout_id`; newest-first) | Yes | `tests/unit/test_services_transaction.py::test_list_transactions_newest_first`, `test_list_transactions_filter_by_date_tree`, `test_list_transactions_filter_by_subcategory_id`, `test_list_transactions_filter_by_hangout_id` |
| **Periodic expenses** (`is_periodic`, `due_day`; type consistency; due = tx in month) | Yes | `tests/unit/test_services_subcategory.py` (`test_create_subcategory_periodic_with_due_day_success`, `test_create_subcategory_periodic_without_due_day_raises_422`, `test_create_subcategory_type_mismatch_raises_422`); `tests/unit/test_services_dashboard.py` (`test_get_due_periodic_expenses_paid_when_transaction_in_month`, etc.) |
| **Dashboard:** cumulative balance, month balance, due periodic expenses | Yes | `tests/unit/test_services_dashboard.py` (`test_get_cumulative_balance_*`, `test_get_month_balance_*`, `test_get_due_periodic_expenses_*`); `tests/integration/test_dashboard_api.py`; Robot — *Dashboard balance returns 200 when AUTH_TOKEN set* |
| **Bulk transactions:** normalized IDs, ownership, all-or-nothing | Yes | `tests/unit/test_services_transaction.py` (`test_bulk_create_transactions_success`, `test_bulk_create_transactions_404_when_subcategory_not_owned`, `test_bulk_create_transactions_404_when_hangout_not_owned`, `test_bulk_create_transactions_all_or_nothing`); `tests/integration/test_transactions_api.py` (`test_bulk_create_transactions_*`) |
| **Import/export:** preview vs existing pairs; CSV oldest→newest, filters | Yes | `tests/unit/test_services_transaction_manager.py` (`test_preview_import_*`, `test_export_transactions_csv_*`); `tests/integration/test_transaction_manager_api.py`; Robot — *Transaction manager export returns 200 when AUTH_TOKEN set* |

**Notes**

- TECHSPEC §1.3 table cites `test_preview_import_*` / `test_export_transactions_csv_*`; implemented names are e.g. `test_preview_import_resolves_valid_row`, `test_export_transactions_csv_oldest_first` — same suites, concrete test names differ slightly from the wildcard wording.
- `tests/unit/test_placeholder.py::test_placeholder` is present but does not map to a §1.3 criterion (harmless leftover).

**Conclusion:** All §1.3 rows are represented by at least one test file or Robot case as required by §6.3.

---

## 2. §8.3 Definition of Done — status and evidence

| §8.3 bullet | Met? | Evidence |
|-------------|------|----------|
| Code matches the phase spec (spec committed before implementation) | **Partially verifiable** | Every phase **01–16** has `.planning/phase-NN-SPEC.md`. This audit did **not** replay full git history to prove each SPEC commit strictly predates its implementation commits (would require per-phase `git log` analysis). |
| All §1.3 cases that apply to the phase are covered; mapping table for test phases | **Met** (project-wide) | §1.3 mapping exists in `TECHSPEC.md` (lines 41–58); section 1 of this file re-verifies coverage against the current test tree. |
| README: run app, run tests (pytest, Robot, ruff), env vars | **Met** | `README.md` — Run (dev), Migrations, Tests and lint (pytest, `pytest --cov`, Robot, Ruff), gate command, env table including `DATABASE_URL`, Auth0, CORS, `TEST_DATABASE_URL`. |
| Gitflow: phase branch merged into `main` | **Partially verifiable** | Audit was run on **`main`** with a complete app matching TECHSPEC. Remote: `origin/main`. Local history shows many `feature/phase-NN-*` branches still present (typical after merge). **Not** proven here that every phase was merged via PR without squash policy review. |
| Gate: `uv run pytest && uv run robot tests/robot && uv run ruff check .` before every commit | **Not verifiable from repo state** | **Evidence this run:** `uv run pytest` — 108 passed; `uv run ruff check .` — all checks passed. **Robot** was not re-run in this audit (requires live `BASE_URL` / optional `AUTH_TOKEN`). Past compliance per commit cannot be proven without CI logs or hooks. |
| Phase SUMMARY: `.planning/phase-NN-SUMMARY.md` before merge | **Met (artifacts)** | **SUMMARY** files exist for phases **01–16** under `.planning/`. |

---

## 3. Phases (ROADMAP) — STATE.md vs code vs SUMMARYs

**`STATE.md`** declares: **Phase 16 — Finance expansion tests & handoff (complete)**; next task none.

**Roadmap source:** `.planning/phase-00-ROADMAP.md` (phases 01–16).

| Phase | Name (ROADMAP) | SPEC | SUMMARY | Consistency with code (high level) |
|------|----------------|------|---------|-----------------------------------|
| 01 | Foundation | Yes | Yes | `app/` layout, FastAPI, CORS, lifespan, `pyproject.toml`, Ruff, tests tree |
| 02 | Data model + migrations | Yes | Yes | `app/models/*`, `alembic/`, SQLAlchemy models |
| 03 | Auth | Yes | Yes | `app/auth.py`, JWT / `get_current_user_id`, protected routes |
| 04 | Categories CRUD | Yes | Yes | `app/routers/category.py`, `app/services/category.py`, schemas |
| 05 | Subcategories CRUD | Yes | Yes | Subcategory router/service; category ownership |
| 06 | Transactions CRUD | Yes | Yes | Transaction router/service; subcategory + hangout ownership |
| 07 | Hangouts CRUD | Yes | Yes | Hangout router/service |
| 08 | Tests & verification | Yes | Yes | Pytest layout, Robot `smoke.robot`, coverage config |
| 09 | Read responses: names not IDs | Yes | Yes | Read schemas with `category_name`, `subcategory_name`, `hangout_name` |
| 10 | Finance expansion spec refresh | Yes | Yes | Doc-only per ROADMAP; TECHSPEC/roadmap alignment |
| 11 | Filtering and sorting | Yes | Yes | List query params on categories, subcategories, transactions; newest-first |
| 12 | Periodic expenses | Yes | Yes | `is_periodic`, `due_day`, validation in subcategory service/schema |
| 13 | Home dashboard APIs | Yes | Yes | `app/routers/dashboard.py`, `app/services/dashboard.py` |
| 14 | Bulk transactions | Yes | Yes | `POST /transactions/bulk` |
| 15 | Transaction manager import/export | Yes | Yes | `app/routers/transaction_manager.py`, import preview + CSV export |
| 16 | Finance expansion tests & handoff | Yes | Yes | `test_openapi_contract.py`, Robot dashboard/export cases, test DB story per `phase-16-SUMMARY.md` |

**Note:** `tests/conftest.py` requires `TEST_DATABASE_URL` to be a **PostgreSQL** URL (`postgresql://...`); otherwise tests are skipped. `README.md` and `.env.example` match that policy. Older phase-16 docs that mentioned SQLite are superseded by the current harness.

---

## 4. README vs §1.5 and §8.3

### §1.5 Repository deliverables

| Deliverable | Status |
|-------------|--------|
| **README:** run app (dev), migrations, tests (pytest, Robot, ruff), env vars, key decisions | **Met** — see `README.md` sections *Run (dev)*, *Migrations*, *Tests and lint*, *Environment variables*, *Key decisions*. |
| **BACKLOG.md** | **Present** at repo root (not exhaustively audited for sync with frontend). |

### §8.3 (README slice)

README documents running the app, migrations, pytest (including coverage), Robot, Ruff, and the gate command — **aligned** with the README bullet in §8.3.

---

## 5. Coverage vs §6.2

**§6.2 asks for:** minimum **80%** lines/statements (and **70%** branches/functions *as decided per phase* / overall).

**Commands run (audit machine, `main`):**

```bash
uv run pytest --cov --cov-report=term-missing -q
uv run pytest --cov --cov-branch -q && uv run coverage report --precision=2
```

**Results**

| Metric | Result | §6.2 threshold | Verdict |
|--------|--------|----------------|---------|
| **Statement / line coverage** (`app/`, `[tool.coverage.run] source = ["app"]`) | **93.04%** total; `fail_under = 80` in `pyproject.toml` **satisfied** | ≥ 80% | **Met** |
| **Lowest modules (statements)** | e.g. `app/auth.py` **65%** statements | Per-file threshold not in TECHSPEC | Overall gate still passes |
| **Branch-aware run** | `coverage report` **TOTAL 90.15%** (combined column with `--cov-branch`) | ≥ 70% branches (soft / overall) | **Met** at aggregate level; some files lower (e.g. `app/services/subcategory.py` **76.47%** in combined report) |

**Robot / full gate:** Not executed in this audit; §6.2 gate string includes Robot — see §8.3 table above.

---

## 6. Summary

- **§1.3:** All criteria map to existing pytest or Robot coverage; this document is the audit-style mapping requested alongside TECHSPEC’s table.
- **§8.3:** README and planning artifacts (SPEC + SUMMARY for 01–16) are in good shape; git ordering of spec vs code and per-commit gate history are **not** fully provable from a static snapshot.
- **Phases:** `STATE.md` and ROADMAP 01–16 align with implemented routers/services and `.planning` SUMMARYs; minor **README vs Phase 16** test-DB wording to reconcile.
- **§6.2:** Pytest coverage on `app/` **exceeds 80%** lines; branch-inclusive report **~90%** total on the same run.
