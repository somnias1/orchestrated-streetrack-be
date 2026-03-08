# Phase 04 — Categories CRUD (Spec)

**Goal:** Router, service, schemas for Categories: list/get/create/update/delete.  
**Key TECHSPEC:** §3.2 (project structure), §4.1 (data model & schema contracts), §4.3 (APIs & contracts).

## Scope

### 1. Schemas (§4.1)

- **CategoryRead**: id (uuid), name, description (str | null), is_income (bool), user_id (str | null).
- **CategoryCreate**: name (required), description (str | null), is_income (bool, default false).
- **CategoryUpdate**: name, description, is_income (all optional).

Location: `app/schemas/category.py`; export from `app/schemas/__init__.py`.

### 2. Service (§3.2)

- **CategoryService** in `app/services/category.py`.
- Methods (static or module-level): accept `db: Session`, `user_id: str`, and ids/body as needed.
- **list(db, user_id, skip=0, limit=50)**: return categories for user_id, ordered (e.g. by name).
- **get_by_id(db, user_id, category_id)**: return one or raise 404 if not found or not owned.
- **create(db, user_id, body: CategoryCreate)**: set user_id from arg, persist, return CategoryRead.
- **update(db, user_id, category_id, body: CategoryUpdate)**: update if owned else 404.
- **delete(db, user_id, category_id)**: delete if owned else 404.
- 404 policy: not found or not owned → HTTPException 404 (no 403).

### 3. Router (§3.2, §4.3)

- **app/routers/category.py**: prefix `/categories`, tags `["categories"]`.
- Dependencies: `get_db`, `CurrentUserId` (from `app.auth`).
- **GET /categories/** — query skip (default 0), limit (default 50) → 200 CategoryRead[].
- **POST /categories/** — body CategoryCreate → 201 CategoryRead.
- **GET /categories/{category_id}** — 200 CategoryRead or 404.
- **PATCH /categories/{category_id}** — body CategoryUpdate → 200 CategoryRead or 404.
- **DELETE /categories/{category_id}** — 204 or 404.
- All endpoints require auth (CurrentUserId); 401 handled by dependency.

### 4. Wire-up

- In `app/main.py`: `include_router(category_router, prefix="/categories", tags=["categories"])` (or equivalent with router’s own prefix/tags).

## Out of scope (Phase 04)

- Subcategories, transactions, hangouts (later phases).
- Pagination metadata beyond skip/limit (TECHSPEC §4.3 list returns array only).
- Unit/integration tests for categories (Phase 08).

## Definition of done

- [ ] Schemas match §4.1; service enforces user scoping and 404 policy.
- [ ] Router exposes all five endpoints; main.py includes router.
- [ ] Gate `uv run pytest && uv run robot tests/robot && uv run ruff check .` passes.
