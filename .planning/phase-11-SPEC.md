# Phase 11 — Filtering and sorting foundation

## Goal (from ROADMAP)

Add list filters for categories, subcategories, and transactions while keeping current response envelopes (CategoryRead[], SubcategoryRead[], TransactionRead[]).

## TECHSPEC scope

- **§1.3**: Categories/Subcategories filters (list by type; subcategories by category_id); Transactions filters (date tree, subcategory_id, hangout_id; newest-first sort). Test coverage for these cases.
- **§4.3**: Implement optional query params on list endpoints as specified in the API table.

## Out of scope this phase

- Dashboard endpoints, bulk transactions, transaction-manager import/export (later phases).
- Changing response envelope shapes.

## Requirements

### Categories — GET /categories/

- Existing: `skip`, `limit` (defaults 0, 50).
- **New optional query:** `is_income` (bool, optional). When provided, filter list to categories where `is_income` equals the given value.
- Response: 200 with `CategoryRead[]`; 401, 422 unchanged.

### Subcategories — GET /subcategories/

- Existing: `skip`, `limit`.
- **New optional query:** `belongs_to_income` (bool, optional). When provided, filter by `belongs_to_income`.
- **New optional query:** `category_id` (UUID, optional). When provided, filter to subcategories whose `category_id` equals the value (must still be user-scoped; category must be owned by user).
- Response: 200 with `SubcategoryRead[]`; 401, 422 unchanged.

### Transactions — GET /transactions/

- Existing: `skip`, `limit`.
- **Default sort:** newest-first (date descending). Already in place; ensure it remains.
- **New optional query:** `year` (int, optional). Filter transactions to this year (date field).
- **New optional query:** `month` (int, 1–12, optional). When used with year (or alone), filter by month.
- **New optional query:** `day` (int, 1–31, optional). When used with year/month (or subset), filter by day. Applied in a date-tree way: year narrows to year; month to month within year; day to day within month.
- **New optional query:** `subcategory_id` (UUID, optional). Filter to transactions for this subcategory (must be user-owned).
- **New optional query:** `hangout_id` (UUID, optional). Filter to transactions linked to this hangout (must be user-owned).
- Response: 200 with `TransactionRead[]`; 401, 422 unchanged.

## Validation

- Optional query params: invalid types (e.g. non-UUID for category_id) yield 422 per FastAPI/Pydantic.
- Date-tree: year/month/day validated as sensible integers (e.g. month 1–12); invalid values yield 422.

## Tests (§1.3)

- Categories: list with no filter returns all; list with `is_income=true` / `is_income=false` returns only matching categories.
- Subcategories: list with `belongs_to_income` and/or `category_id` filters returns only matching subcategories (user-scoped).
- Transactions: list with year/month/day (date tree), subcategory_id, hangout_id returns filtered set; order is newest-first (date desc).
- Existing list/get/create/update/delete tests remain passing; no regression.

## Definition of done (per TECHSPEC §8.3)

- This spec committed before any implementation code.
- Branch `feature/phase-11-filtering-and-sorting-foundation` used for all work.
- Gate `uv run pytest && uv run robot tests/robot && uv run ruff check .` passes before every commit.
- phase-11-SUMMARY.md written; STATE.md updated to Phase 11 complete; merge to main with --no-ff.
