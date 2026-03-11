# Phase 13 — Home dashboard read APIs

## Goal (from ROADMAP)

Add separate endpoints for cumulative balance, selected-month balance, and due periodic expenses.

## TECHSPEC scope

- **§1.3** Success criteria: Dashboard — independent endpoints expose cumulative balance, selected-month balance, and due periodic expenses for a selected month; test coverage mapping (Dashboard row TBD → Phase 13/16).
- **§3.6** Dashboard split: Home metrics stay split into three endpoints so the frontend can fetch/render them independently.
- **§4.3** Dashboard APIs:
  - GET `/dashboard/balance` — no query; 200: `DashboardBalanceRead`; 401.
  - GET `/dashboard/month-balance` — query `year`, `month` (required); 200: `DashboardMonthBalanceRead`; 401, 422.
  - GET `/dashboard/due-periodic-expenses` — query `year`, `month` (required); 200: `DashboardDuePeriodicExpenseRead[]`; 401, 422.

## Out of scope

- Bulk transactions, import/export, transaction manager (Phases 14–15).
- Changes to existing CRUD or filters.

## Deliverables

1. **Schemas** (§4.1): `DashboardBalanceRead`, `DashboardMonthBalanceRead`. `DashboardDuePeriodicExpenseRead` already exists.
2. **Service** (`app/services/dashboard.py`): `get_cumulative_balance(db, user_id) -> DashboardBalanceRead`; `get_month_balance(db, user_id, year, month) -> DashboardMonthBalanceRead`. `get_due_periodic_expenses` already exists.
3. **Router**: New `app/routers/dashboard.py` with prefix `/dashboard`, three GET endpoints, all protected (CurrentUserId). Register in `app/main.py`.
4. **Balance semantics**: Net balance = sum of transaction values for income subcategories minus sum for expense subcategories (same unit as `Transaction.value`). Cumulative = all time; month = transactions in given (year, month).
5. **Tests**: Unit tests for balance service functions; integration tests for the three HTTP endpoints (auth, 422 for missing year/month where required). Update §1.3 mapping for Dashboard row.

## Schema field definitions

- **DashboardBalanceRead**: `balance: int` — cumulative net (income − expense) in same unit as Transaction.value.
- **DashboardMonthBalanceRead**: `balance: int`, `year: int`, `month: int` — net for the selected month.
- **DashboardDuePeriodicExpenseRead**: (existing) subcategory_id, subcategory_name, category_id, category_name, due_day, paid.

## Definition of Done

- Spec committed before any implementation code.
- Gate `uv run pytest && uv run robot tests/robot && uv run ruff check .` passes before every commit.
- All three endpoints return correct shapes; month-balance and due-periodic-expenses require year, month and return 422 when missing/invalid.
- Phase summary and STATE.md updated; branch merged to main with --no-ff.
