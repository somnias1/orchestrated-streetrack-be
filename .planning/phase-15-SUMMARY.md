# Phase 15 — Transaction manager import/export

## What was built

- **Import:** POST `/transaction-manager/import` accepts `TransactionImportRequest` (rows with category_name, subcategory_name, value, description, date, optional hangout_id). Each row is resolved against the user’s existing category/subcategory pairs; valid rows become `TransactionCreate`; unresolved or invalid (e.g. hangout not owned) rows are reported in `invalid_rows`. Response is `TransactionImportPreview` (transactions + invalid_rows), ready for the client to call POST `/transactions/bulk`.
- **Export:** GET `/transaction-manager/export` with optional query params (year, month, day, subcategory_id, hangout_id) returns `text/csv` with header and transaction rows, ordered **oldest to newest**.

## Files changed

- **.planning/phase-15-SPEC.md:** Phase scope, import/export contracts, implementation tasks.
- **app/schemas/transaction.py:** Added `TransactionImportRow`, `TransactionImportRequest`, `TransactionImportInvalidRow`, `TransactionImportPreview`.
- **app/services/transaction_manager.py:** New module with `preview_import()` and `export_transactions_csv()`.
- **app/routers/transaction_manager.py:** New router for POST `/import` and GET `/export`.
- **app/main.py:** Included `transaction_manager_router`.
- **tests/unit/test_services_transaction_manager.py:** Unit tests for preview (resolve ok, pair not found, hangout not owned, mixed valid/invalid) and export (empty, oldest-first order, year filter).
- **tests/integration/test_transaction_manager_api.py:** Integration tests for import (200 with payload, invalid_rows, 401) and export (200 CSV, 401).

## Decisions made

- Import uses **category_name + subcategory_name** only (no category_id/subcategory_id in the request); resolution is strictly against the authenticated user’s categories and subcategories.
- Optional **hangout_id** in each import row is validated for ownership; invalid hangout yields an entry in `invalid_rows` (row_index + message), not 404 for the whole request.
- Export uses the same filter params as the transaction list (year, month, day, subcategory_id, hangout_id) and returns all matching rows in ascending date order (oldest first) per §1.3.
- CSV columns: date, subcategory_id, subcategory_name, value, description, hangout_id, hangout_name.

## Tests added

- **tests/unit/test_services_transaction_manager.py:**  
  `test_preview_import_resolves_valid_row`, `test_preview_import_invalid_pair_reported`, `test_preview_import_mixed_valid_invalid`, `test_preview_import_hangout_not_owned_reported`, `test_preview_import_with_owned_hangout`, `test_export_transactions_csv_empty`, `test_export_transactions_csv_oldest_first`, `test_export_transactions_csv_filtered_by_year`.
- **tests/integration/test_transaction_manager_api.py:**  
  `test_import_preview_200_returns_payload`, `test_import_preview_invalid_pair_invalid_rows`, `test_import_preview_without_auth_returns_401`, `test_export_returns_csv_200`, `test_export_without_auth_returns_401`.

## §1.3 case verification (import/export)

| §1.3 case | Tool | Location |
|-----------|------|----------|
| Import: preview vs existing pairs; invalid rows reported | pytest | tests/unit/test_services_transaction_manager.py (preview_import_*), tests/integration/test_transaction_manager_api.py (import_preview_*) |
| Export: date-filtered CSV, oldest to newest | pytest | tests/unit/test_services_transaction_manager.py (export_*), tests/integration/test_transaction_manager_api.py (export_*) |

## Known issues / follow-ups

- None. Phase 16 will extend the §1.3 mapping table and add any further Robot/coverage for the finance expansion.

---

## Post-merge update (FK RESTRICT / back propagation)

- **ORM & DB:** Category→Subcategory and Subcategory→Transaction foreign keys changed from `ondelete="CASCADE"` to `ondelete="RESTRICT"`. Relationship cascades changed from `cascade="all, delete-orphan"` to `cascade="save-update, merge"` with `passive_deletes=True` so deletes are not propagated; the DB enforces referential integrity.
- **Migration:** `alembic/versions/b1c4e8f2a0d3_fk_restrict_category_subcategory.py` — upgrades both FKs to RESTRICT; downgrade restores CASCADE.
- **API behavior:** Delete category returns **409 Conflict** when the category has subcategories; delete subcategory returns **409 Conflict** when it has transactions. Detail messages direct the client to remove or reassign children first. Services check for children before delete and catch `IntegrityError` as a fallback.
- **Tests:** `test_delete_category_409_when_has_subcategories`, `test_delete_subcategory_409_when_has_transactions` (unit).
- **Files changed:** `app/models/category.py`, `app/models/subcategory.py`, `app/models/transaction.py`, `app/services/category.py`, `app/services/subcategory.py`, `tests/unit/test_services_category.py`, `tests/unit/test_services_subcategory.py`, new migration.
