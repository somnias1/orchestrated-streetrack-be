# Technical Specification (TECHSPEC) — Streetrack Backend

> **GSD-aligned.** This spec drives the phase-based development pipeline (see FRAMEWORK.md). Keep it the single source of technical truth; ROADMAP and STATE.md should stay consistent with it.

---

## 1. Problem & Context

### 1.1 Problem Statement

Users need a **personal finance / expense-tracking** application. The **backend** (streetrack-be) must expose a REST API that the frontend (streetrack-fe) consumes. Money flows are organized into **Categories** (e.g. Food, Transport, Salary) and **Subcategories**; **Transactions** record individual entries and can be linked to **Subcategories** and **Hangouts** (e.g. outings or events). All data is **user-scoped**: the backend enforces ownership via **Auth0 JWT** (the `sub` claim is the user id). The backend must provide CRUD for categories, subcategories, transactions, and hangouts; validate every protected request with Auth0; and return only data belonging to the authenticated user.

### 1.2 Goals (GSD: what must be TRUE when done)

- **FastAPI** app with CORS, health and root endpoints; lifespan for DB engine.
- **PostgreSQL** with **SQLAlchemy 2** and **Alembic**; UUID primary keys; `user_id` on all four resources (Auth0 `sub`).
- **Auth0 JWT** validation and a **CurrentUserId** dependency; all mutable endpoints require a valid Bearer token.
- **CRUD** for **Categories**, **Subcategories**, **Transactions**, and **Hangouts** with strict user scoping: list/get only own rows; create/update/delete only own resources; subcategory create/update only if category belongs to user; transaction create/update only if subcategory and (when present) hangout belong to user.
- List endpoints support **`skip`** and **`limit`** query params (defaults 0, 50).
- Post-v1 finance expansion adds **filtering/sorting** for list endpoints, **periodic expense** metadata on subcategories, **Home/dashboard** read endpoints for balance and due expenses, **bulk transaction creation**, and **transaction import/export** flows.
- **OpenAPI** exposed at `/openapi.json` for the frontend.
- **Spec-first, phase-driven** development: phase specs committed before implementation; git history reflects the pipeline.

### 1.3 Success Criteria (observable) & Test Coverage

- **Auth**: Valid token yields `user_id` (sub); invalid or missing token yields **401**.
- **Categories**: List/get/create/update/delete scoped by `user_id`; **404** when resource exists but belongs to another user.
- **Subcategories**: Same; create/update only allowed when the referenced category belongs to the user.
- **Transactions**: Same; create/update only when subcategory (and optional hangout) belong to the user.
- **Hangouts**: List/get/create/update/delete scoped by `user_id`; 404 when not owned.
- **API contract**: Responses match Pydantic schemas; **422** on validation errors with `detail: ValidationError[]`.
- **Categories/Subcategories filters**: list endpoints can filter by movement type; subcategories can also filter by `category_id`.
- **Transactions filters**: list endpoint supports date-tree filtering (`year`, `month`, `day`) plus `subcategory_id` and `hangout_id`, with newest-first default sorting.
- **Periodic expenses**: subcategories can be marked `is_periodic` with `due_day`; `due_day` is required only for periodic subcategories; category/subcategory type flags must match.
- **Dashboard**: independent endpoints expose cumulative balance, selected-month balance, and due periodic expenses for a selected month.
- **Bulk transactions**: normalized-ID bulk creation validates ownership first and is all-or-nothing.
- **Import/export**: import validates pasted sheet rows against existing category/subcategory pairs and returns a payload ready for bulk creation; export returns date-filtered CSV ordered oldest to newest.

**Test coverage mapping** (filled Phase 08; audit verifies each row):

| §1.3 case | Tool | Location (file / suite) |
|-----------|------|-------------------------|
| Auth: valid token → user_id | pytest | tests/unit/test_auth.py::test_valid_token_returns_user_id |
| Auth: invalid token → 401 | pytest | tests/unit/test_auth.py::test_invalid_token_raises_401 |
| Auth: missing token → 401 | pytest | tests/unit/test_auth.py::test_missing_token_raises_401, tests/integration/test_auth_401.py |
| Categories: list/get/create/update/delete scoped | pytest | tests/unit/test_services_category.py, tests/integration/test_categories_api.py |
| Categories: 404 when not owned | pytest | tests/unit/test_services_category.py, tests/integration/test_categories_api.py::test_categories_get_404_when_not_owned |
| Subcategories: CRUD + category ownership | pytest | tests/unit/test_services_subcategory.py, tests/integration/test_subcategories_api.py |
| Transactions: CRUD + subcategory/hangout ownership | pytest | tests/unit/test_services_transaction.py, tests/integration/test_transactions_api.py |
| Hangouts: CRUD scoped | pytest | tests/unit/test_services_hangout.py, tests/integration/test_hangouts_api.py |
| API contract: 422 validation error shape | pytest | tests/integration/test_auth_401.py::test_validation_error_returns_422_detail |
| Smoke + one flow per resource (status, structure) | Robot | tests/robot/smoke.robot |
| Categories/Subcategories filters: list by type; subcategories by category_id | pytest | TBD Phase 11/16 |
| Transactions filters: date tree, subcategory_id, hangout_id; newest-first sort | pytest | TBD Phase 11/16 |
| Periodic expenses: is_periodic, due_day validation; type consistency | pytest | TBD Phase 12/16 |
| Dashboard: cumulative balance, month balance, due periodic expenses | pytest | TBD Phase 13/16 |
| Bulk transactions: normalized-ID batch, ownership check, all-or-nothing | pytest | TBD Phase 14/16 |
| Import/export: import preview vs existing pairs; export date-filtered CSV | pytest | TBD Phase 15/16 |

### 1.4 Out of Scope (current)

- Rate limiting; audit log; frontend (lives in streetrack-fe).

### 1.5 Repository Deliverables

- **README**: How to run the app (dev, migrations), run tests (pytest, Robot, ruff), env vars, key decisions.
- **BACKLOG.md**: Kept in sync with streetrack-fe; Done / High / Medium / Later for backend.

### 1.6 BACKLOG Alignment

The **BACKLOG.md** at repo root is the full-stack backlog. Backend-relevant mapping:

| BACKLOG area | Backend scope | TECHSPEC sections | Phases (example) |
|--------------|---------------|-------------------|------------------|
| **Done** | FastAPI, CORS, Postgres, Alembic, Auth0, CRUD all four, schemas, config, names in read responses | §1.2, §3, §4 | 01–09 |
| **High** | Filtering/sorting, periodic expenses, dashboard reads, bulk transactions, import/export | §1.2, §1.3, §4.1, §4.3 | 10–15 |
| **Medium** | Pagination metadata; validation/error shape polish; OpenAPI polish | §4.3, §5 | Post–finance expansion |
| **Later** | Rate limiting; audit log | §1.4, §4 | Future |

List endpoints support **`?skip`** and **`?limit`**; document in README and .env.example.

---

## 2. Tech Stack & Constraints

### 2.1 Runtime & Platform

| Area | Choice | Notes |
|------|--------|-------|
| **Runtime** | Python 3.14+ | Pin in pyproject.toml. |
| **Framework** | FastAPI | API, OpenAPI, dependency injection. |
| **Database** | PostgreSQL | Via SQLAlchemy 2 + psycopg2. |
| **Package / deps** | uv | pyproject.toml, uv.lock; no ^ or ~. |
| **Lint / format** | Ruff | Lint and format in one. |

### 2.2 Core Dependencies & Versions

Pin **exact** versions in `pyproject.toml` (no `^` or `~`). Reference values:

| Package | Version (min) | Purpose |
|---------|---------------|---------|
| fastapi[standard] | 0.129.0 | API, OpenAPI, CORS. |
| sqlalchemy | 2.0.0 | ORM. |
| alembic | 1.14.0 | Migrations. |
| pydantic-settings | (from fastapi[standard]) | Config from env. |
| python-jose[cryptography] | 3.3.0 | JWT verify, JWKS. |
| requests | 2.32.0 | JWKS fetch. |
| psycopg2-binary | 2.9.9 | PostgreSQL driver. |

**Dev / test** (add as dev dependencies):

| Package | Purpose |
|---------|---------|
| pytest | Unit and integration tests. |
| pytest-cov | Coverage. |
| httpx | FastAPI TestClient (ASGI). |
| robotframework | Acceptance / API tests. |
| robotframework-requests | HTTP keywords for Robot. |

### 2.3 Hard Constraints

- **Spec-driven development**: Create and commit phase spec (`.planning/phase-NN-SPEC.md`) before implementing; git history must show spec before code.
- **Gitflow**: Each phase on a **feature branch** from `main` (e.g. `feature/phase-NN-<slug>`). Merge to `main` at phase end. No phase complete until branch is merged.
- **Gate before every commit**: `uv run pytest && uv run robot tests/robot && uv run ruff check .` must pass on the phase branch. (Adjust `tests/robot` if Robot suite lives elsewhere.)
- **Line endings**: `.gitattributes` with `* text=auto eol=lf` from Phase 01 to avoid CRLF breaking Ruff.
- **No secrets in repo**: Use `.env` and `.env.example`; do not commit secrets.
- **Exact dependency versions** in pyproject.toml; no `^` or `~`.

### 2.4 Preferences (soft)

- All application code under **`app/`**; Pydantic for schemas and settings; session-per-request (no global session).

---

## 3. Architecture

### 3.1 High-Level Architecture

- Single **FastAPI** application; CORS configured from settings; **lifespan**: create engine (and optionally `Base.metadata.create_all` or rely on Alembic), dispose on shutdown.
- **Request flow**: Bearer token → **get_current_user_id** (Auth0 JWT validation) → router → **service** (receives `user_id`) → SQLAlchemy session → PostgreSQL. All mutable endpoints require authentication; only **GET /** and **GET /health** are unsecured.

### 3.2 Project Structure

All application source under **`app/`**. Root holds config, docs, tooling.

- **Entry**: `app/main.py` — FastAPI app, CORS, lifespan, `include_router` for each resource.
- **Routers**: `app/routers/` — one module per resource (category, subcategory, transaction, hangout); prefix and tags; `Depends(get_db)`, `CurrentUserId`.
- **Services**: `app/services/` — one module per resource; service classes with static methods; accept `db`, `user_id`, and resource ids/body; enforce ownership.
- **Models**: `app/models/` — SQLAlchemy declarative models (Category, Subcategory, Transaction, Hangout).
- **Schemas**: `app/schemas/` — Pydantic Create, Update, Read per resource.
- **DB**: `app/db/` — base (DeclarativeBase, get_engine, session_factory), config (Settings from env), session (get_db).
- **Auth**: `app/auth.py` — Auth0 JWKS fetch, JWT validation, get_current_user_id, CurrentUserId type alias.
- **Tests**: `tests/` at repo root (pytest: unit, integration); `tests/robot/` for Robot Framework (`.robot` files).
- **Root**: pyproject.toml, uv.lock, alembic.ini, .env.example, TECHSPEC.md, FRAMEWORK.md, STATE.md, BACKLOG.md.

```
[ROOT]/
├── app/
│   ├── main.py
│   ├── auth.py
│   ├── db/           # base, config, session
│   ├── models/       # Category, Subcategory, Transaction, Hangout
│   ├── schemas/      # Create, Update, Read per resource
│   ├── services/     # CategoryService, etc.
│   └── routers/      # category, subcategory, transaction, hangout
├── tests/
│   ├── unit/
│   ├── integration/
│   └── robot/        # .robot files
├── alembic/
├── pyproject.toml
├── uv.lock
├── .env.example
├── TECHSPEC.md
├── FRAMEWORK.md
├── STATE.md
└── BACKLOG.md
```

### 3.3 Key Boundaries & Conventions

- **DB access**: All access via session from **get_db**; no global session.
- **Protected routes**: All list/get/create/update/delete use **CurrentUserId**; unsecured only `/`, `/health`.
- **Services**: Never trust client for `user_id`; always receive it from the dependency.
- **404 policy**: When resource is not found or not owned by the user, return **404** (no 403 to avoid leaking existence).
- **List endpoints**: Accept query params **`skip`**, **`limit`** (defaults 0, 50).
- **Type consistency**: `category.is_income` and `subcategory.belongs_to_income` must match whenever a subcategory is created or updated.
- **Periodic expenses**: `due_day` is valid only when `is_periodic=true`; due status is determined by whether the selected month contains at least one transaction for that subcategory.
- **Dashboard design**: keep Home reads split into separate endpoints so heavier balance or due-expense queries do not block unrelated cards.
- **Request/response**: Pydantic schemas; OpenAPI auto-generated by FastAPI.

### 3.4 API Surface Summary

- **Unsecured**: GET `/`, GET `/health`.
- **Categories**: GET/POST `/categories/`, GET/PATCH/DELETE `/categories/{id}`.
- **Subcategories**: GET/POST `/subcategories/`, GET/PATCH/DELETE `/subcategories/{id}`.
- **Transactions**: GET/POST `/transactions/`, GET/PATCH/DELETE `/transactions/{id}`.
- **Transactions bulk**: POST `/transactions/bulk`.
- **Hangouts**: GET/POST `/hangouts/`, GET/PATCH/DELETE `/hangouts/{id}`.
- **Dashboard**: GET `/dashboard/balance`, GET `/dashboard/month-balance`, GET `/dashboard/due-periodic-expenses`.
- **Transaction manager**: POST `/transaction-manager/import`, GET `/transaction-manager/export`.

Detailed contract table in §4.3.

### 3.5 Request Body Validation

- Request bodies validated via **Pydantic**; invalid payloads return **422** with `detail: ValidationError[]`. No frontend forms in this repo.

### 3.6 Complexity Exceptions

- **Dashboard split**: Home metrics are intentionally split into three endpoints instead of one aggregate response so the frontend can fetch/render them independently and each query can evolve without coupling the others.

### 3.7 API Design Guidelines

(Replaces UI/UX for backend.)

- **Request/response**: JSON; Content-Type application/json.
- **Status codes**: **200** (get, list, update), **201** (create), **204** (delete), **401** (missing or invalid token), **404** (not found or not owned), **422** (validation error).
- **422 body**: `{ "detail": [ { "loc": ["body", "field"], "msg": "...", "type": "..." } ] }` (Pydantic/OpenAPI standard).
- **OpenAPI**: Available at **GET /openapi.json** once the app is running; source of truth for the frontend.
- **No UI** in this repo; this is the API-only backend.

---

## 4. Data & APIs

### 4.1 Data Model (ORM and schema contracts)

All resources are **user-scoped**; `user_id` is set from the Auth0 token and may appear in Read schemas. All IDs are **UUIDs**.

#### Category

| Schema | Fields | Notes |
|--------|--------|--------|
| **Read** | id (uuid), name, description (str \| null), is_income (bool), user_id (str \| null) | Returned by list, get, create, update. |
| **Create** | name (required), description (str \| null), is_income (bool, default false) | user_id from token. |
| **Update** | name, description, is_income (all optional) | PATCH body. |

**ORM**: id (UUID PK), user_id (str, nullable), name, description (str, nullable, 1024), is_income (bool). One-to-many Subcategory.

#### Subcategory

| Schema | Fields | Notes |
|--------|--------|--------|
| **Read** | id, category_id (uuid), category_name (str), name, description (str \| null), belongs_to_income (bool), is_periodic (bool), due_day (int \| null), user_id (str \| null) | Read responses expose category_id and category_name (FE uses id for lookups). |
| **Create** | category_id (uuid, required), name (required), description (str \| null), belongs_to_income (bool, default false), is_periodic (bool, default false), due_day (int \| null) | user_id from token; `due_day` required only when `is_periodic=true`. |
| **Update** | category_id, name, description, belongs_to_income, is_periodic, due_day (all optional) | PATCH body. |

**ORM**: id (UUID PK), category_id (FK category.id CASCADE), user_id, name, description (str, nullable, 1024), belongs_to_income (bool), is_periodic (bool), due_day (int, nullable). Many-to-one Category; one-to-many Transaction.

#### Transaction

| Schema | Fields | Notes |
|--------|--------|--------|
| **Read** | id, subcategory_id (uuid), subcategory_name (str), value (int), description (str), date (date), hangout_id (uuid \| null), hangout_name (str \| null), user_id (str \| null) | Read responses expose ids and names (FE uses ids for lookups). |
| **Create** | subcategory_id (uuid, required), value (int, required), description (str, required), date (date, required), hangout_id (uuid \| null) | user_id from token. |
| **Update** | subcategory_id, value, description, date, hangout_id (all optional) | PATCH body. |

**ORM**: id (UUID PK), subcategory_id (FK subcategory.id CASCADE), value, description, date, hangout_id (FK hangout.id SET NULL, nullable), user_id. Many-to-one Subcategory, optional Hangout.

#### Hangout

| Schema | Fields | Notes |
|--------|--------|--------|
| **Read** | id, name, description (str \| null), date (date), user_id (str \| null) | User-scoped. |
| **Create** | name (required), date (date, required), description (str \| null) | user_id from token. |
| **Update** | name, date, description (all optional) | PATCH body. |

**ORM**: id (UUID PK), name, description (str, nullable, 1024), date, user_id. One-to-many Transaction.

#### Common error shapes

- **422**: `{ "detail": [ {"loc": [...], "msg": "...", "type": "..."} ] }` (Pydantic ValidationError).

### 4.2 Storage

| Concern | Choice | Notes |
|---------|--------|-------|
| **Database** | PostgreSQL | Via SQLAlchemy 2. |
| **Migrations** | Alembic | Schema versioning. Create revisions with **autogenerate**: `uv run alembic revision --autogenerate -m "description"`. Apply with `uv run alembic upgrade head`. |
| **Session** | Per request (get_db) | No global session; no in-memory cache requirement for v1. |

### 4.3 APIs & Contracts (backend implements)

The backend **implements** the following. OpenAPI at **GET /openapi.json** is the runtime source of truth; this table is the spec for implementation.

List endpoints accept optional **`?skip`** and **`?limit`** (defaults 0, 50). All path IDs are UUIDs. For list filtering, use optional query params rather than separate search endpoints.

| Method | Path | Request | Response | Errors |
|--------|------|---------|----------|--------|
| **Categories** |
| GET | `/categories/` | query: skip?, limit?, is_income? | 200: CategoryRead[] | 401, 422 |
| POST | `/categories/` | body: CategoryCreate | 201: CategoryRead | 401, 422 |
| GET | `/categories/{category_id}` | path | 200: CategoryRead | 401, 404 |
| PATCH | `/categories/{category_id}` | path + body: CategoryUpdate | 200: CategoryRead | 401, 404, 422 |
| DELETE | `/categories/{category_id}` | path | 204 | 401, 404 |
| **Subcategories** |
| GET | `/subcategories/` | query: skip?, limit?, belongs_to_income?, category_id? | 200: SubcategoryRead[] | 401, 422 |
| POST | `/subcategories/` | body: SubcategoryCreate | 201: SubcategoryRead | 401, 404, 422 |
| GET | `/subcategories/{subcategory_id}` | path | 200: SubcategoryRead | 401, 404 |
| PATCH | `/subcategories/{subcategory_id}` | path + body: SubcategoryUpdate | 200: SubcategoryRead | 401, 404, 422 |
| DELETE | `/subcategories/{subcategory_id}` | path | 204 | 401, 404 |
| **Transactions** |
| GET | `/transactions/` | query: skip?, limit?, year?, month?, day?, subcategory_id?, hangout_id? | 200: TransactionRead[] | 401, 422 |
| POST | `/transactions/` | body: TransactionCreate | 201: TransactionRead | 401, 404, 422 |
| POST | `/transactions/bulk` | body: TransactionBulkCreate | 201: TransactionRead[] | 401, 404, 422 |
| GET | `/transactions/{transaction_id}` | path | 200: TransactionRead | 401, 404 |
| PATCH | `/transactions/{transaction_id}` | path + body: TransactionUpdate | 200: TransactionRead | 401, 404, 422 |
| DELETE | `/transactions/{transaction_id}` | path | 204 | 401, 404 |
| **Hangouts** |
| GET | `/hangouts/` | query: skip?, limit? | 200: HangoutRead[] | 401 |
| POST | `/hangouts/` | body: HangoutCreate | 201: HangoutRead | 401, 422 |
| GET | `/hangouts/{hangout_id}` | path | 200: HangoutRead | 401, 404 |
| PATCH | `/hangouts/{hangout_id}` | path + body: HangoutUpdate | 200: HangoutRead | 401, 404, 422 |
| DELETE | `/hangouts/{hangout_id}` | path | 204 | 401, 404 |
| **Dashboard** |
| GET | `/dashboard/balance` | none | 200: DashboardBalanceRead | 401 |
| GET | `/dashboard/month-balance` | query: year, month | 200: DashboardMonthBalanceRead | 401, 422 |
| GET | `/dashboard/due-periodic-expenses` | query: year, month | 200: DashboardDuePeriodicExpenseRead[] | 401, 422 |
| **Transaction manager** |
| POST | `/transaction-manager/import` | body: TransactionImportRequest | 200: TransactionImportPreview | 401, 404, 422 |
| GET | `/transaction-manager/export` | query: year?, month?, day?, subcategory_id?, hangout_id? | 200: text/csv | 401, 422 |

### 4.4 Authentication

- **Mechanism**: **Auth0 JWT** (OAuth2/OIDC). Validate using JWKS from Auth0 domain; extract **`sub`** as `user_id`.
- **Dependency**: **get_current_user_id** — returns `sub` or raises **401** when token is missing, invalid, or expired.
- **Protected routes**: All list/get/create/update/delete require valid Bearer token. No roles/scopes in v1.

---

## 5. Non-Functional Requirements

### 5.1 Performance

- List endpoints paginated via **skip**/ **limit**; no caching requirement for v1.
- Home/dashboard reads stay split by concern so heavier aggregate queries do not delay unrelated cards in the frontend.

### 5.2 Security

- JWT validation on all protected routes; **user_id** never taken from client; no PII in logs.

### 5.3 Accessibility

- N/A for API; document status codes and error shape for frontend consumers.

### 5.4 Observability

- Optional logging; no PII; no mandatory monitoring for v1.

---

## 6. Testing Strategy

### 6.1 Test Pyramid

| Level | Tool | Scope |
|-------|------|-------|
| **Unit** | pytest | Auth (get_current_user_id: valid/invalid/missing token, mocked JWKS/jose); services (Category, Subcategory, Transaction, Hangout) with mocked or in-memory DB — CRUD and user scoping, 404 for wrong user. |
| **Integration** | pytest | FastAPI TestClient; hit real endpoints with overridden get_db and auth (inject user_id); at least one flow per resource (list, get, create, update, delete); 401 without token, 404 for wrong user. |
| **Acceptance / API** | Robot Framework | High-level tests calling the API (or TestClient via adapter); verify status codes, response structure, key behaviors (e.g. create category → list returns it; invalid token → 401). Scope: smoke + one flow per resource. |

- **Gate**: No real backend required for pytest; Robot may run against a running app or a test server started in CI.

### 6.2 Coverage & Gates

- **Pytest coverage**: Minimum **80%** lines/statements, **70%** branches/functions on code touched by the phase (or overall, as decided per phase). Verify with `uv run pytest --cov`.
- **Gate command**: `uv run pytest && uv run robot tests/robot && uv run ruff check .` must pass **before every commit** on the phase branch. Audit prompt runs pytest with coverage and Robot and reports vs this section.

### 6.3 Verification (GSD goal-backward)

- All §1.3 test cases are covered by a pytest test or a Robot test; **mapping table** (see §1.3) produced in the test phase. DoD requires this table.

### 6.4 Pytest Setup

- **Layout**: e.g. `tests/unit/`, `tests/integration/`; `conftest.py` for get_db override, auth override, TestClient (httpx.ASGITransport).
- **Deps**: Pin pytest, pytest-cov, httpx in pyproject.toml (dev). Ensure test files are not shipped in the application package.

### 6.5 Robot Framework Setup

- **Location**: `tests/robot/` with `.robot` files.
- **Run**: e.g. `uv run robot --variable BASE_URL:http://localhost:8000 tests/robot` (or use a test server in CI). Variables: BASE_URL; optional AUTH_TOKEN for protected endpoints (from env or CI).
- **Library**: RequestsLibrary or custom keywords (requests/httpx). Scope: smoke (health, root) + one flow per resource (create → list/get). No production secrets in repo.

---

## 7. Deployment & Environment

### 7.1 Environments

| Env | Purpose | Config |
|-----|---------|--------|
| **Local** | Development | `.env`; `uv run uvicorn app.main:app --reload`. |
| **CI** | Tests + lint | `uv run pytest`, `uv run robot tests/robot`, `uv run ruff check .`. |

### 7.2 Build & Release

- **Run (dev)**: `uv run uvicorn app.main:app --reload`.
- **Run (prod)**: `uv run uvicorn app.main:app`.
- **Migrations (apply)**: `uv run alembic upgrade head`. Requires `DATABASE_URL`.
- **Migrations (create)**: After model changes, `uv run alembic revision --autogenerate -m "description"`; review and apply. See README.
- No frontend-style “build”; this is API-only.

### 7.3 Environment Variables & Secrets

- **DATABASE_URL**: PostgreSQL connection string (e.g. `postgresql://user:pass@host:5432/dbname`).
- **AUTH0_DOMAIN**, **AUTH0_AUDIENCE**, **AUTH0_ISSUER** (optional): Auth0 JWT validation.
- **CORS_ALLOWED_ORIGINS**: Comma-separated origins for CORS.
- Document in **.env.example**; do not commit secrets.

---

## 8. GSD Integration Notes

### 8.1 Phase → TECHSPEC Mapping

| Phase (example from ROADMAP) | Primary TECHSPEC sections |
|-----------------------------|----------------------------|
| 01 Foundation | §2, §3.2 — scaffold, deps, tooling, app structure, .gitattributes |
| 02 Data model + migrations | §4.1, §4.2 — models, Alembic, initial migration |
| 03 Auth | §3.1, §4.4 — Auth0 JWT, get_current_user_id, CurrentUserId |
| 04 Categories CRUD | §3.2, §4.1, §4.3 — router, service, schemas, endpoints |
| 05 Subcategories CRUD | §4.1, §4.3 — ownership check (category) |
| 06 Transactions CRUD | §4.1, §4.3 — ownership check (subcategory, hangout) |
| 07 Hangouts CRUD | §4.1, §4.3 |
| 08 Tests & verification | §1.3, §6 — pytest + Robot, coverage, §1.3 mapping table |
| 09 Read responses: names not IDs | §4.1, §4.3 — enriched read schemas for FE lookups |
| 10 Finance expansion spec refresh | §1.2, §1.3, §4.1, §4.3 — new contracts and roadmap rows |
| 11 Filtering and sorting foundation | §1.3, §4.3 — categories, subcategories, transactions query filters |
| 12 Periodic expenses | §1.3, §4.1, §4.3 — subcategory fields, validation, due-status logic |
| 13 Home dashboard read APIs | §1.3, §3.6, §4.3 — split balance and due-expense endpoints |
| 14 Bulk transactions | §1.3, §4.3 — normalized-ID batch creation |
| 15 Transaction manager import/export | §1.3, §4.3 — import preview and CSV export |
| 16 Finance expansion tests & handoff | §1.3, §6, §8.3 — coverage and FE contract verification |

(Actual phases come from `.planning/phase-00-ROADMAP.md` generated at bootstrap.)

### 8.2 Plan Constraints for Agents

- All app source under **`app/`**; tests under **`tests/`**.
- All protected routes use **CurrentUserId**; services receive **user_id** from dependency only.
- **Spec-first**: Create and commit `.planning/phase-NN-SPEC.md` **before** implementation. No code without a committed spec.
- **Pre-flight checklist**: At phase start, agent prints phase name, branch name, spec file, **gate** `uv run pytest && uv run robot tests/robot && uv run ruff check .` and **waits for user confirmation** before coding.
- **Gitflow**: Feature branch from `main`; merge at phase end. Phase not done until branch is merged.
- **Gate per commit**: Gate must pass before every commit on the phase branch.

### 8.3 Definition of Done (per phase)

- Code matches the phase spec (spec committed before implementation).
- All §1.3 test cases that apply to the phase are covered; mapping table produced for test phases.
- README documents how to run app, run tests (pytest, Robot, ruff), and env vars.
- **Gitflow complete**: Phase branch merged into `main`.
- **Gate**: `uv run pytest && uv run robot tests/robot && uv run ruff check .` passed before every commit.
- **Phase SUMMARY**: `.planning/phase-NN-SUMMARY.md` committed before merge; no phase complete without it.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-03-09 | Phase 10 complete: §1.3 test coverage mapping extended with finance expansion cases (filters, periodic, dashboard, bulk, import/export) — locations TBD Phase 11–16. |
| 2026-03-09 | Phase 10 planning: TECHSPEC expanded for filtering/sorting, periodic expenses, split dashboard endpoints, bulk transactions, and transaction manager import/export. |
| 2026-03-08 | Phase 09: §4.1 Read schemas — SubcategoryRead and TransactionRead expose both ids and names (FE uses ids for lookups). |
| 2026-03-XX | BE TECHSPEC created: full rewrite for streetrack-be. §1 Problem & Context (API, user scoping, Auth0, CRUD). §2 Tech stack (Python, uv, FastAPI, Ruff, pytest, Robot). §3 Architecture (app structure, conventions, §3.7 API design guidelines). §4 Data & APIs (ORM/schema contracts, storage, endpoint table, auth). §5–§8 NFRs, testing (pytest + Robot), deployment, GSD integration. Gate: `uv run pytest && uv run robot tests/robot && uv run ruff check .`. Aligned with FRAMEWORK.md for bootstrap and phase-driven development from scratch. |
