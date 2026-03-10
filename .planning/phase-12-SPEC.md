# Phase 12 — Periodic expenses

## Goal (from ROADMAP)

Add subcategory periodic-expense fields, validation, and due-status business rules.

## TECHSPEC scope

- **§1.3**: Periodic expenses — subcategories can be marked `is_periodic` with `due_day`; `due_day` required only for periodic subcategories; category/subcategory type flags must match. Test coverage: is_periodic, due_day validation, type consistency.
- **§4.1**: Subcategory ORM and schema contracts — add `is_periodic` (bool), `due_day` (int, nullable). Read/Create/Update per §4.1 table.
- **§4.3**: Validation and type consistency enforced on create/update; API contract unchanged (same endpoints).
- **Due-status rule** (§3.3): A periodic subcategory is considered **paid for a selected month** if and only if at least one transaction exists for that subcategory in that month. Implement this rule in the service layer (for use by Phase 13 dashboard endpoint).

## Out of scope this phase

- Dashboard HTTP endpoints (Phase 13). Only the business logic for “paid for month” is implemented here.
- Bulk transactions, import/export (later phases).

## Requirements

### 1. Data model (Subcategory)

- **ORM**: Add `is_periodic: Mapped[bool]` (default False), `due_day: Mapped[int | None]` (nullable integer).
- **Migration**: Autogenerate with `uv run alembic revision --autogenerate -m "add subcategory is_periodic and due_day"`; apply with `uv run alembic upgrade head`.

### 2. Schemas

- **SubcategoryRead**: Add `is_periodic: bool`, `due_day: int | None`.
- **SubcategoryCreate**: Add `is_periodic: bool = False`, `due_day: int | None = None`. Validation: `due_day` required when `is_periodic=true` (Pydantic model validator or field validator).
- **SubcategoryUpdate**: Add `is_periodic: bool | None = None`, `due_day: int | None = None`. Same validation when both or is_periodic is set: if effective is_periodic is true, due_day must be provided (or already set on existing row for PATCH).

### 3. Validation

- **due_day when is_periodic**: On create, if `is_periodic=true` then `due_day` must be present and valid (e.g. 1–31). On update, if setting `is_periodic=true` (or leaving it true), ensure `due_day` is set (either in body or already on row); if clearing is_periodic, due_day can be ignored/cleared.
- **Type consistency**: On create and update, `subcategory.belongs_to_income` must match `category.is_income` for the (possibly updated) category. Return 422 with a clear message if mismatch.

### 4. Due-status business logic

- Implement a function (e.g. in subcategory or a small dashboard-oriented module) that, given `user_id`, `year`, and `month`, returns the list of user’s **periodic** subcategories with a **paid** flag for that month: **paid** ⇔ at least one transaction for that subcategory in that (year, month). Signature and return type to be chosen so Phase 13 can call it from GET `/dashboard/due-periodic-expenses` without further logic.

### 5. Service and router

- **create_subcategory**: Persist `is_periodic`, `due_day`; enforce type consistency with category before insert.
- **update_subcategory**: Apply `is_periodic`, `due_day`; enforce type consistency when category_id or belongs_to_income changes; enforce due_day when is_periodic is or becomes true.
- **_row_to_read**: Include `is_periodic` and `due_day` in SubcategoryRead.

## Tests (§1.3)

- **is_periodic / due_day**: Create subcategory with `is_periodic=true` and valid `due_day` (e.g. 15) → 201, response includes is_periodic and due_day. Create with `is_periodic=true` and missing or invalid due_day → 422.
- **due_day optional when not periodic**: Create with `is_periodic=false` and no due_day → 201. Create with is_periodic=false and due_day=15 → 201 (due_day stored or ignored per spec).
- **Type consistency**: Create subcategory with belongs_to_income that does not match category.is_income → 422. Update subcategory or category so they mismatch → 422 (or equivalent test for update path).
- **Due-status rule**: Unit test: for a user with one periodic subcategory, no transaction in month M → paid=false; one transaction in month M for that subcategory → paid=true.
- Existing subcategory and transaction CRUD tests remain passing; gate passes before every commit.

## Definition of done (per TECHSPEC §8.3)

- This spec committed before any implementation code.
- Branch `feature/phase-12-periodic-expenses` used for all work.
- Gate `uv run pytest && uv run robot tests/robot && uv run ruff check .` passes before every commit.
- phase-12-SUMMARY.md written; STATE.md updated to Phase 12 complete; merge to main with --no-ff.
