# Phase 19 — Transactions list pagination

## Goal (from ROADMAP)

Align **`GET /transactions/`** with the same pagination envelope as categories, subcategories, and hangouts: **`PaginatedRead[TransactionRead]`** — `items`, `total`, `skip`, `limit`, `has_more`, and **`next_skip`**. Preserve existing query filters (`year`, `month`, `day`, `subcategory_id`, `hangout_id`) and **newest-first** ordering.

## TECHSPEC refs

- §4.3 — endpoint table; pagination envelope subsection (includes transactions).
- §1.3 — list pagination success criteria; test mapping for transactions list.

## Implementation notes

- **Service**: Build a single filtered `where_clause` (user_id + optional filters); `COUNT(*)` for `total`; `SELECT` with `order_by(date.desc()).offset(skip).limit(limit)`; return **`paginated_read(...)`** from `app/schemas/pagination.py`.
- **Router**: `response_model=PaginatedRead[TransactionRead]` (bulk and single create unchanged).
- **Tests**: Unit tests use `.items` / `.total`; integration and Robot read list from **`items`**; add or extend a unit test for `total` / `skip` / `has_more` / `next_skip` across pages.
- **OpenAPI**: Contract test asserts `GET` on `/transactions/` remains exposed.

## Out of scope

- Keyset/cursor pagination; changing default `skip`/`limit`; `POST /transactions/` and `POST /transactions/bulk` response shapes.

## Done when

- Gate passes: `uv run pytest && uv run robot tests/robot && uv run ruff check .`
- `TECHSPEC.md` §1.3 / §4.3 / §8.1 / changelog aligned; `phase-19-SUMMARY.md` and `STATE.md` updated.
