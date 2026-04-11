# Phase 20 — Transaction CSV export format

## What was built

- **`GET /transaction-manager/export`** CSV rows use: `date` (`dd/mm/yyyy`), `$` (literal USD column), `value`, `category_name`, `subcategory_name`, `description`, `hangout_name`. Row order remains oldest to newest; filters unchanged.
- **Query loading:** Nested `joinedload` on subcategory and category avoids N+1 when resolving category names.

## Files changed

- **TECHSPEC.md** (on `main` before implementation): §1.2–1.3, §4.3 CSV semantics, §1.3 mapping, §8.1 Phase 20, changelog.
- **.planning/phase-00-ROADMAP.md**, **STATE.md**: Phase 20 row and session state.
- **.planning/phase-20-SPEC.md**: Committed before code; contract for headers and columns.
- **app/services/transaction_manager.py**: `export_transactions_csv` column layout and `joinedload(Subcategory.category)`.
- **tests/unit/test_services_transaction_manager.py**, **tests/integration/test_transaction_manager_api.py**: Assertions for new CSV shape.

## Decisions made

- Header row uses exact names `date`, `$`, `value`, `category_name`, `subcategory_name`, `description`, `hangout_name` (aligned with TECHSPEC §4.3).
- Import API (`POST /transaction-manager/import`) unchanged; clients that parsed the old export (IDs + ISO dates) must migrate to the new columns.

## Tests added

- Unit export tests updated: header row, `dd/mm/yyyy`, `$` and category columns, ordering, year filter.
- Integration `test_export_returns_csv_200` parses CSV and asserts column values for a sample transaction.

## Known issues / follow-ups

- None.
