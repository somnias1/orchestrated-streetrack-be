# Phase 17 — Name filters + pagination envelope

## Goal (from ROADMAP)

Add optional `name` query param with case-insensitive substring (`icontains`) semantics on list endpoints for categories, subcategories, and hangouts. Change those three list responses from a raw JSON array to a pagination envelope: `items`, `total`, `skip`, `limit`. Do **not** add `has_more` / `next_skip` (Phase 18). Leave `GET /transactions/` response shape unchanged (still a JSON array).

## TECHSPEC refs

- §4.3 — `?name` on `GET /categories/`, `GET /subcategories/`, `GET /hangouts/`; `PaginatedRead[T]` base fields for those lists.
- §1.3 — extend tests for new filters and envelope (pytest; Robot list steps if AUTH_TOKEN set).

## Implementation notes

- **Filter**: When `name` is omitted, no name filter. When present (including empty string), apply `ILIKE '%<value>%'` on the resource `name` column (categories, subcategories, hangouts).
- **Total**: Count rows matching `user_id` and all active filters (including `name`), **before** `skip`/`limit`.
- **Echo**: Return the same `skip` and `limit` as requested (defaults 0 and 50 per TECHSPEC).
- **Schema**: Shared generic `PaginatedRead[T]` in `app/schemas/`; routers use `PaginatedRead[CategoryRead]`, etc.

## Out of scope

- Transactions list contract.
- Phase 18 convenience fields (`has_more`, `next_skip`).

## Done when

- Gate passes: `uv run pytest && uv run robot tests/robot && uv run ruff check .`
- `phase-17-SUMMARY.md` and `STATE.md` updated before merge.
