# Phase 11 — Filtering and sorting foundation

## What was built

- **Categories list**: Optional query param `is_income` (bool). When provided, response is filtered to categories with that `is_income` value.
- **Subcategories list**: Optional query params `belongs_to_income` (bool) and `category_id` (UUID). Filter by movement type and/or category.
- **Transactions list**: Optional query params `year`, `month` (1–12), `day` (1–31), `subcategory_id`, `hangout_id`. Date-tree filtering via SQL extract; month/day validated with Query(ge/le). Default sort remains **newest-first** (date desc).
- **Response envelopes**: Unchanged (CategoryRead[], SubcategoryRead[], TransactionRead[]).
- **Tests**: Unit tests for all filters and for newest-first order; §1.3 mapping in TECHSPEC updated with concrete locations.

## Files changed

| File | Why |
|------|-----|
| .planning/phase-11-SPEC.md | New: phase scope (filters + sort; §1.3, §4.3). |
| app/routers/category.py | Added optional `is_income` query param. |
| app/services/category.py | Filter by `is_income` when provided. |
| app/routers/subcategory.py | Added optional `belongs_to_income`, `category_id`. |
| app/services/subcategory.py | Apply optional filters. |
| app/routers/transaction.py | Added optional year, month, day, subcategory_id, hangout_id; Query(ge=1, le=12) for month, Query(ge=1, le=31) for day. |
| app/services/transaction.py | Date-tree filters via extract(); subcategory_id, hangout_id filters; order_by date desc (unchanged). |
| tests/unit/test_services_category.py | test_list_categories_filter_by_is_income. |
| tests/unit/test_services_subcategory.py | test_list_subcategories_filter_by_belongs_to_income, test_list_subcategories_filter_by_category_id. |
| tests/unit/test_services_transaction.py | test_list_transactions_newest_first, test_list_transactions_filter_by_date_tree, test_list_transactions_filter_by_subcategory_id, test_list_transactions_filter_by_hangout_id. |
| TECHSPEC.md | §1.3 mapping: Categories/Subcategories filters and Transactions filters rows point to new tests. |
| .planning/phase-11-SUMMARY.md | This summary. |

## Decisions made

- **Date-tree**: year/month/day applied as independent SQL extract() filters (no “month requires year”); month and day validated 1–12 and 1–31 via FastAPI Query to return 422 for invalid values.
- **Import order**: Ruff required sqlalchemy.orm before sqlalchemy.sql in transaction service.

## Tests added

- **Category**: test_list_categories_filter_by_is_income — list with is_income true/false returns only matching categories.
- **Subcategory**: test_list_subcategories_filter_by_belongs_to_income, test_list_subcategories_filter_by_category_id — filter by type and by category_id.
- **Transaction**: test_list_transactions_newest_first (order date desc), test_list_transactions_filter_by_date_tree (year, month, day), test_list_transactions_filter_by_subcategory_id, test_list_transactions_filter_by_hangout_id.

## Known issues / follow-ups

- None. Phase 12 (periodic expenses) can build on current list filters.
