# Streetrack – Full-stack backlog

Single backlog for **streetrack-be** (backend) and **streetrack-fe** (frontend). Move items to **Done** as you complete them. Priorities: **virtualization** and **unit tests** first; **import/export** last.

---

## Done

### Backend (streetrack-be)

- [x] GSD bootstrap: STATE.md, .planning/, phase-00-ROADMAP.md (phases 01–08 defined; no app code yet)
- [x] Phase 01 — Foundation
- [x] Phase 02 — Data model + migrations
- [x] Phase 03 — Auth
- [x] Phase 04 — Categories CRUD
- [x] Phase 05 — Subcategories CRUD
- [x] Phase 06 — Transactions CRUD
- [x] Phase 07 — Hangouts CRUD
- [x] Phase 08 — Tests & verification
- [x] Phase 09 — Read responses: names not IDs

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

- [ ] **Phase 10 — Finance expansion spec refresh:** TECHSPEC, roadmap, STATE, and backlog aligned for the finance stream
- [ ] **Phase 11 — Filtering and sorting foundation:** categories by type, subcategories by type/category, transactions by date tree/subcategory/hangout
- [ ] **Phase 12 — Periodic expenses:** `is_periodic`, `due_day`, type consistency, due-status rules
- [ ] **Phase 13 — Home dashboard read APIs:** separate endpoints for cumulative balance, selected-month balance, and due periodic expenses
- [ ] **Phase 14 — Bulk transactions:** strict normalized-ID bulk creation
- [ ] **Phase 15 — Transaction manager import/export:** import preview from pasted sheet data and CSV export
- [ ] **Phase 16 — Finance expansion tests & handoff:** pytest, integration, robot coverage where practical, FE contract verification

### Frontend

- [ ] **Phase 18 — UX/UI improvements:** Type as MUI Chips; Transactions: Button+Menu (Transaction / Bulk); default current-month filter for transactions; Hangouts table action colors (primary/error)
- [ ] **Phase 19 — List filters and sort:** Categories by type; Subcategories by type and category; Transactions by date tree, subcategory, hangout; sort by date (newest first); default current month on Transactions
- [ ] **Phase 20 — Subcategory periodic expenses:** is_periodic, due_day in form and list
- [ ] **Phase 21 — Home dashboard:** Balance, month balance, due periodic expenses (dashboard API client + Home screen)
- [ ] **Phase 22 — Bulk transactions:** BulkTransactionsDialog and POST /transactions/bulk
- [ ] **Phase 23 — Transaction manager import/export UI:** Import (paste → preview → bulk); Export (date-filtered CSV download)
- [ ] **Phase 24 — Finance expansion tests and polish:** Tests for dashboard, bulk, import/export, filters, periodic; §1.3 mapping; coverage gate

---

## Medium priority

### Backend

- [ ] Pagination metadata (e.g. total count, next/prev) for list endpoints if needed
- [ ] Consistent validation messages and error response shape for frontend
- [ ] Optional: OpenAPI tags/descriptions for docs

### Frontend

- [ ] Loading and error states refinements (e.g. per-action feedback in CRUD flows)
- [ ] Optional: layout and navigation polish

---

## Later / Nice to have

### Backend

- [ ] Rate limiting or abuse protection if needed
- [ ] Optional: audit log or “last updated” for sensitive operations

### Frontend

- [ ] **Import/export UI** (Phase 23 covers main flow; below are refinements)
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
5. **Import/export**: keep backend-first, but only after filters and bulk transaction creation are stable.

---

_Last updated: FE ROADMAP extended with Phases 18–24 (finance stream). Backend at Phase 10 — Finance expansion spec refresh (in progress). Copy to streetrack-fe BACKLOG.md to keep repos in sync._
