# Phase 05 — Subcategories CRUD (Spec)

**Goal:** CRUD + category ownership checks.  
**Key TECHSPEC:** §4.1 (data model, schema contracts), §4.3 (APIs & contracts).  
**Depends on:** Phase 04 (Categories CRUD).

---

## Scope

1. **Schemas (§4.1)**  
   - **SubcategoryRead**: id, category_id (uuid), name, description (str | null), belongs_to_income (bool), user_id (str | null).  
   - **SubcategoryCreate**: category_id (uuid, required), name (required), description (str | null), belongs_to_income (bool, default false).  
   - **SubcategoryUpdate**: category_id, name, description, belongs_to_income (all optional).

2. **Service (§4.1, §4.3)**  
   - `app/services/subcategory.py`: list, get, create, update, delete scoped by `user_id`.  
   - **Ownership rule:** Create/update only allowed when the referenced **category** belongs to the user; otherwise 404.  
   - List/get/delete: subcategory must be owned by user (or not found → 404).

3. **Router (§4.3)**  
   - GET `/subcategories/` — query `skip`, `limit` (defaults 0, 50); 200 SubcategoryRead[].  
   - POST `/subcategories/` — body SubcategoryCreate; 201 SubcategoryRead; 401, 404 (category not owned), 422.  
   - GET `/subcategories/{subcategory_id}` — 200 SubcategoryRead; 401, 404.  
   - PATCH `/subcategories/{subcategory_id}` — body SubcategoryUpdate; 200 SubcategoryRead; 401, 404, 422.  
   - DELETE `/subcategories/{subcategory_id}` — 204; 401, 404.

4. **App**  
   - Include subcategory router in `app/main.py` (prefix `/subcategories`, tags).

---

## Out of scope this phase

- Transactions CRUD (Phase 06).  
- Hangouts CRUD (Phase 07).  
- New migrations (Subcategory table already exists from Phase 02).

---

## Definition of done (Phase 05)

- [ ] Schemas SubcategoryRead, SubcategoryCreate, SubcategoryUpdate in `app/schemas/subcategory.py` and exported from `app/schemas/__init__.py`.  
- [ ] Service with category ownership check on create/update; 404 when category not found or not owned.  
- [ ] Router with all five endpoints; gate passes before every commit.
