# Phase 18 — Pagination convenience fields

## What was built

- **`PaginatedRead`** (`app/schemas/pagination.py`): `has_more` and `next_skip`; shared **`paginated_read()`** helper computes hints from `total`, `skip`, `limit`, and `len(items)` per TECHSPEC §4.3.
- **Services** `list_categories`, `list_subcategories`, `list_hangouts` return the helper-built envelope (transactions list unchanged).

## Files changed

- `app/schemas/pagination.py` — new fields + `paginated_read`.
- `app/services/category.py`, `subcategory.py`, `hangout.py` — use `paginated_read`.
- `tests/unit/test_pagination.py` — pure helper cases.
- `tests/unit/test_services_category.py`, integration `test_categories_api.py`, `test_subcategories_api.py`, `test_hangouts_api.py` — envelope assertions.
- `TECHSPEC.md` — §1.3, §4.3 wording, §1.3 mapping, §8.1 phase row, changelog.

## Decisions made

- **`has_more`**: `skip + len(items) < total`.
- **`next_skip`**: `skip + limit` when `has_more`, else `None` (JSON `null`).

## Tests added

- `tests/unit/test_pagination.py` — empty page, multi-page sequence.
- Extended category service + categories/subcategories/hangouts integration tests for `has_more` / `next_skip`.

## Known issues / follow-ups

- None.
