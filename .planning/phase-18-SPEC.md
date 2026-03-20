# Phase 18 — Pagination convenience fields

## Goal (from ROADMAP)

Add server-side next-page hints on the existing pagination envelope for `GET /categories/`, `GET /subcategories/`, and `GET /hangouts/`: **`has_more`** and **`next_skip`** so the frontend does not derive “next page” from `total`, `skip`, and `limit`.

## TECHSPEC refs

- §4.3 — `PaginatedRead[T]` includes `has_more` and `next_skip` (`null` when no next page).
- §1.3 — success criteria and test mapping for list envelope behavior.

## Semantics

- **`has_more`**: `true` iff more matching rows exist after the current page: `skip + len(items) < total`.
- **`next_skip`**: When `has_more` is `true`, the `skip` value the client should send for the next page: `skip + limit` (echoed request `limit`). When `has_more` is `false`, **`null`** (JSON `null`).

## Implementation notes

- Extend `app/schemas/pagination.py` (`PaginatedRead` and/or a small builder) so all three list services stay consistent.
- Transactions list remains a raw array (unchanged).

## Out of scope

- Cursor / keyset pagination; changing default `skip`/`limit`; transactions list shape.

## Done when

- Gate passes: `uv run pytest && uv run robot tests/robot && uv run ruff check .`
- `TECHSPEC.md` §1.3 / changelog aligned; `phase-18-SUMMARY.md` and `STATE.md` updated before merge.
