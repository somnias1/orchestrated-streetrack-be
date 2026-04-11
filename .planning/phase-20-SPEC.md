# Phase 20 — Transaction CSV export format

## Goal

Change `GET /transaction-manager/export` CSV output to match TECHSPEC §4.3: human-oriented columns with European date format and a fixed USD symbol column, without changing query parameters or response `Content-Type`.

## CSV contract

### Header row (exact column order)

1. `date`
2. `$` (header is the dollar sign; second column identifies USD)
3. `value`
4. `category_name`
5. `subcategory_name`
6. `description`
7. `hangout_name`

### Data rows

- **Order:** Oldest transaction date first (ascending `Transaction.date`), unchanged from Phase 15.
- **date:** `dd/mm/yyyy` (e.g. `01/03/2025` for 2025-03-01).
- **Second column (`$`):** Every data row contains exactly the character `$` (USD marker only; monetary amount remains in `value`).
- **value:** Integer as stored on the transaction (same semantics as API).
- **category_name:** From the subcategory’s parent category; empty string if category relationship is missing (should not occur for valid FK data).
- **subcategory_name:** From loaded subcategory; empty if missing.
- **description:** Transaction description; `csv.writer` handles quoting for commas/quotes.
- **hangout_name:** Hangout name if present; empty string when `hangout_id` is null.

### Filters

Same optional query params as today: `year`, `month`, `day`, `subcategory_id`, `hangout_id`. User-scoped via `user_id`.

### Implementation notes

- Use nested `joinedload(Transaction.subcategory).joinedload(Subcategory.category)` (plus existing hangout load) to avoid N+1 queries.

## Non-goals

- **Import** (`POST /transaction-manager/import`) format and validation unchanged.
- No new endpoints or migrations.

## Verification

- Unit tests in `tests/unit/test_services_transaction_manager.py` for export: header shape, date format, `$` column, category name, ordering, year filter.
- Integration test `test_export_returns_csv_200` updated for new CSV shape.
