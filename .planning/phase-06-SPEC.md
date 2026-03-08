# Phase 06 — Transactions CRUD (Spec)

**Goal:** CRUD + subcategory and optional hangout ownership.  
**Key TECHSPEC:** §4.1 (data model, schema contracts), §4.3 (APIs & contracts).  
**Depends on:** Phase 05 (Subcategories CRUD).

---

## Scope

1. **Schemas (§4.1)**  
   - **TransactionRead**: id, subcategory_name (str), value (int), description (str), date (date), hangout_name (str | null), user_id (str | null).  
   - **TransactionCreate**: subcategory_id (uuid, required), value (int, required), description (str, required), date (date, required), hangout_id (uuid | null).  
   - **TransactionUpdate**: subcategory_id, value, description, date, hangout_id (all optional).

2. **Service (§4.1, §4.3)**  
   - `app/services/transaction.py`: list, get, create, update, delete scoped by `user_id`.  
   - **Ownership rules:** Create/update only allowed when the referenced **subcategory** belongs to the user; when **hangout_id** is present, that hangout must also belong to the user; otherwise 404.  
   - List/get/delete: transaction must be owned by user (or not found → 404).

3. **Router (§4.3)**  
   - GET `/transactions/` — query `skip`, `limit` (defaults 0, 50); 200 TransactionRead[].  
   - POST `/transactions/` — body TransactionCreate; 201 TransactionRead; 401, 404 (subcategory/hangout not owned), 422.  
   - GET `/transactions/{transaction_id}` — 200 TransactionRead; 401, 404.  
   - PATCH `/transactions/{transaction_id}` — body TransactionUpdate; 200 TransactionRead; 401, 404, 422.  
   - DELETE `/transactions/{transaction_id}` — 204; 401, 404.

4. **App**  
   - Include transaction router in `app/main.py` (prefix `/transactions`, tags).

---

## Out of scope this phase

- Hangouts CRUD (Phase 07).  
- New migrations (Transaction table already exists from Phase 02).

---

## Definition of done (Phase 06)

- [x] Schemas TransactionRead, TransactionCreate, TransactionUpdate in `app/schemas/transaction.py` and exported from `app/schemas/__init__.py`.  
- [x] TransactionRead exposes subcategory_name and hangout_name (not subcategory_id, hangout_id) in list/get/create/update responses (implemented in Phase 09).  
- [x] Service with subcategory (and optional hangout) ownership check on create/update; 404 when not found or not owned.  
- [x] Router with all five endpoints; gate passes before every commit.
