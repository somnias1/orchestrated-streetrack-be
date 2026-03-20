# Phase 17 — Name filters + pagination envelope

## What was built

- **`PaginatedRead[T]`** (`app/schemas/pagination.py`): `items`, `total`, `skip`, `limit` (no `has_more` / `next_skip` — Phase 18).
- **List endpoints** `GET /categories/`, `GET /subcategories/`, `GET /hangouts/` now return that envelope and accept optional query param **`name`** with SQL `ILIKE '%value%'` (icontains) on the resource `name` column.
- **Services** compute `total` with the same filters as the page query, before `skip`/`limit`.
- **`GET /transactions/`** unchanged (still a JSON array).

## Files changed

- `app/schemas/pagination.py` — new shared envelope schema.
- `app/services/category.py`, `subcategory.py`, `hangout.py` — filters, count, `PaginatedRead` return.
- `app/routers/category.py`, `subcategory.py`, `hangout.py` — `response_model`, `name` query param.
- `tests/unit/test_services_*.py` — envelope assertions; new name-filter tests; pagination total/skip test for categories.
- `tests/integration/test_categories_api.py`, `test_hangouts_api.py`, `test_subcategories_api.py` — envelope JSON shape.
- `tests/robot/smoke.robot` — list length via `items`.
- `TECHSPEC.md` — §1.3 success criteria + mapping row, changelog, §8.1 phase row.

## Decisions made

- **`name=None`**: no name filter. Any other string (including empty) applies `ilike` with `%value%` (empty → matches all rows), consistent with SPEC.

## Tests added

- Unit: `test_list_categories_filter_by_name_icontains`, `test_list_categories_pagination_total_and_skip`; `test_list_subcategories_filter_by_name_icontains`; `test_list_hangouts_filter_by_name_icontains`.
- Integration: existing flows updated for envelope keys.
- Robot: `Get Length` on `${r.json()}[items]` for the three resources.

## Known issues / follow-ups

- Phase 18: `has_more` and `next_skip` on the same envelope (TECHSPEC §4.3).
