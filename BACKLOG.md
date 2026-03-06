# Streetrack – Full-stack backlog

Single backlog for **streetrack-be** (backend) and **streetrack-fe** (frontend). Move items to **Done** as you complete them. Priorities: **virtualization** and **unit tests** first; **import/export** last.

---

## Done

### Backend (streetrack-be)

- [x] GSD bootstrap: STATE.md, .planning/, phase-00-ROADMAP.md (phases 01–08 defined; no app code yet)

### Frontend (streetrack-fe)

- [x] Auth0: login, callback, logout, protected routes, token in API client
- [x] Session persistence (localStorage cache), no login flash on refresh
- [x] Layout with navigation (Home, Categories, Subcategories, Transactions, Hangouts)
- [x] Home and basic routing; centralized routes (`src/routes.ts`)
- [x] Categories: full CRUD UI (create, edit, delete; form dialog with Zod, delete confirmation)
- [x] Subcategories: list (virtualized table), service, store, full CRUD UI (category picker, forms)
- [x] Transactions: list (virtualized table), service, store, full CRUD UI (subcategory/hangout pickers)
- [x] Hangouts: list (virtualized table), service, store, full CRUD UI (form + delete dialogs)
- [x] API client with Bearer token (callbackApi); all list endpoints use `skip`/`limit`
- [x] Tailwind + MUI, theme helper for Tailwind colors in `sx`
- [x] Unit/integration tests: Vitest, RTL, MSW — auth, API client, all four resources (services, stores, screens, CRUD flows); coverage gate (80% lines/statements, 70% branches/functions)
- [x] **Phase 13:** TanStack React Query for all list/CRUD; hooks in services; modules use hooks; Zustand as global read mirror synced from query
- [x] **Phase 14:** Theme, layout & Categories table alignment — tweakcn-style theme, light/dark toggle, table state row min height
- [x] **Phase 15:** Remaining screens & CRUD — Subcategories, Transactions, Hangouts table state alignment; theme tokens verified
- [x] **Phase 16:** Tests & coverage gate — §1.3 mapping; 80% lines/statements, 70% branches/functions; gate passing
- [x] **Bugfixes (Phase 04/07/08):** Virtual table full-width alignment (categoriesTable, transactionsTable, hangoutsTable) per VIRTUAL-TABLE-SIZING-FIX.md

---

## High priority

### Backend

- [ ] **Phase 01 — Foundation:** Project scaffold, deps (uv, pyproject.toml), tooling (Ruff), app structure per §3.2, .gitattributes
- [ ] **Phase 02 — Data model + migrations:** ORM models (Category, Subcategory, Transaction, Hangout), Alembic, initial migration
- [ ] **Phase 03 — Auth:** Auth0 JWT validation, `get_current_user_id`, `CurrentUserId` dependency
- [ ] **Phase 04 — Categories CRUD:** Router, service, schemas, list/get/create/update/delete (user-scoped)
- [ ] **Phase 05 — Subcategories CRUD:** CRUD + category ownership check
- [ ] **Phase 06 — Transactions CRUD:** CRUD + subcategory and optional hangout ownership
- [ ] **Phase 07 — Hangouts CRUD:** CRUD (user-scoped)
- [ ] **Phase 08 — Tests & verification:** Pytest + Robot, coverage gate, §1.3 mapping table
- [ ] **Unit tests** (Phase 08)
  - [ ] Auth: JWT validation, `get_current_user_id` (valid / invalid / missing token)
  - [ ] Services: CategoryService CRUD (user scoping, 404 for wrong user)
  - [ ] Services: SubcategoryService (category ownership)
  - [ ] Services: TransactionService (subcategory/hangout ownership)
  - [ ] Services: HangoutService CRUD
  - [ ] Routers: at least one endpoint per resource (list, get, create) with mocked DB + auth
  - [ ] Optional: integration tests (test client + DB or in-memory SQLite)

### Frontend

- [ ] Optional: layout/UX refinements; keyboard/a11y for virtualized tables and dialogs

---

## Medium priority

### Backend

- [ ] Pagination metadata (e.g. total count, next/prev) for list endpoints if needed
- [ ] Consistent validation messages and error response shape for frontend
- [ ] Optional: filtering/sorting for transactions (date, category, etc.)
- [ ] Optional: OpenAPI tags/descriptions for docs

### Frontend

- [ ] Loading and error states refinements (e.g. per-action feedback in CRUD flows)
- [ ] Optional: layout and navigation polish

---

## Later / Nice to have

### Backend

- [ ] **Import/export (clipboard, defined format)**
  - [ ] Define format (e.g. JSON or CSV: categories, subcategories, transactions, hangouts)
  - [ ] Export: endpoint (or action) returning current user’s data in that format (for clipboard or download)
  - [ ] Import: endpoint accepting same format; validate and create/update scoped to current user
  - [ ] Idempotency / conflict handling (by id or business key) if needed
- [ ] Rate limiting or abuse protection if needed
- [ ] Optional: audit log or “last updated” for sensitive operations

### Frontend

- [ ] **Import/export UI**
  - [ ] “Copy to clipboard” (export in defined format)
  - [ ] “Paste from clipboard” (parse and call import API)
  - [ ] Clear feedback on success and validation errors
- [ ] Reports or dashboards (e.g. spending by category, by period)
- [ ] Offline / PWA if relevant

---

## How to use this backlog

1. **Backend** repo: `streetrack-be`. **Frontend** repo: `streetrack-fe`. This same `BACKLOG.md` lives in both repos—keep them in sync when you update.
2. Move tasks from High / Medium / Later into **Done** as you complete them.
3. **Virtualization**: Frontend has virtualized lists for categories, subcategories, transactions, and hangouts. Backend supports `?skip=` and `?limit=` on list endpoints.
4. **Unit tests**: Frontend has Vitest/RTL/MSW tests and coverage gate. Backend unit tests remain High priority.
5. **Import/export**: do after core CRUD and tests. Define the format once; implement backend first, then frontend clipboard/UI.

---

_Last updated: Backend at Phase 01 — Foundation (in progress). GSD bootstrap complete (STATE.md, .planning/, phase-00-ROADMAP.md); no app code yet. Copy to streetrack-fe BACKLOG.md to keep repos in sync._
