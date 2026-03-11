# Phase 13 — Home dashboard read APIs

## What was built

- **Schemas**: `DashboardBalanceRead` (balance: int), `DashboardMonthBalanceRead` (balance, year, month). `DashboardDuePeriodicExpenseRead` already existed from Phase 12.
- **Service**: `get_cumulative_balance(db, user_id)` — net balance = sum(income transaction values) − sum(expense transaction values) for all user transactions. `get_month_balance(db, user_id, year, month)` — same logic restricted to transactions in that month. `get_due_periodic_expenses` already existed.
- **Router**: `app/routers/dashboard.py` with prefix `/dashboard`. GET `/dashboard/balance` (no query); GET `/dashboard/month-balance` (query year, month required); GET `/dashboard/due-periodic-expenses` (query year, month required). All protected; month endpoints validate year (1–9999) and month (1–12), return 422 when missing/invalid.
- **Tests**: Unit tests for get_cumulative_balance (empty, income minus expense) and get_month_balance (empty month, only-in-month). Integration tests for all three endpoints: 401 without auth; 200 and response shape; 422 for missing year or month on month-balance and due-periodic-expenses.

## Files changed

| File | Why |
|------|-----|
| .planning/phase-13-SPEC.md | New: phase scope (goal, §1.3, §3.6, §4.3; schema field definitions; DoD). |
| app/schemas/dashboard.py | Added DashboardBalanceRead, DashboardMonthBalanceRead. |
| app/services/dashboard.py | Added get_cumulative_balance, get_month_balance (join Transaction → Subcategory, case on belongs_to_income for sign). |
| app/routers/dashboard.py | New: three GET endpoints, CurrentUserId, Query(ge/le) for year/month. |
| app/main.py | include_router(dashboard_router). |
| tests/unit/test_services_dashboard.py | test_get_cumulative_balance_empty, test_get_cumulative_balance_income_minus_expense, test_get_month_balance_empty_month, test_get_month_balance_only_in_month. |
| tests/integration/test_dashboard_api.py | New: 401 for balance/month-balance/due-periodic-expenses; 200 shape; 422 for missing year/month. |
| TECHSPEC.md | §1.3 mapping: Dashboard row updated with test locations. |
| .planning/phase-13-SUMMARY.md | This summary. |

## Decisions made

- **Balance semantics**: Net = income (belongs_to_income) transaction values minus expense transaction values; same unit as Transaction.value. Cumulative = all time; month = date in [start, end) for that (year, month).
- **Month validation**: FastAPI Query(ge=1, le=12) for month and (ge=1, le=9999) for year so invalid values return 422.

## Tests added

- **Unit**: test_get_cumulative_balance_empty; test_get_cumulative_balance_income_minus_expense; test_get_month_balance_empty_month; test_get_month_balance_only_in_month.
- **Integration**: test_dashboard_balance_without_auth_returns_401; test_dashboard_balance_returns_shape; test_dashboard_month_balance_without_auth_returns_401; test_dashboard_month_balance_returns_shape; test_dashboard_month_balance_missing_year_422; test_dashboard_month_balance_missing_month_422; test_dashboard_due_periodic_expenses_without_auth_returns_401; test_dashboard_due_periodic_expenses_returns_list; test_dashboard_due_periodic_expenses_missing_year_422; test_dashboard_due_periodic_expenses_missing_month_422.

## Known issues / follow-ups

- None.
