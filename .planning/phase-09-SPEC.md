# Phase 09 — Read responses: names not IDs (Spec)

**Goal:** SubcategoryRead returns category_name; TransactionRead returns subcategory_name and hangout_name (instead of IDs in read responses).  
**Key TECHSPEC:** §4.1 (schema contracts), §4.3 (APIs & contracts).  
**Depends on:** Phase 05 (Subcategories CRUD), Phase 06 (Transactions CRUD), Phase 08 (Tests).

---

## Scope

This phase extends the **read** (response) contracts of Phase 05 and Phase 06. Create/Update request bodies keep using IDs; only the read schemas and the way responses are built change.

1. **Subcategories (extends Phase 05)**  
   - **SubcategoryRead**: Expose `category_name` (str) instead of `category_id`.  
   - Service: When returning SubcategoryRead (list, get, create, update), eager-load `Subcategory.category` and set `category_name = row.category.name`.  
   - No change to SubcategoryCreate or SubcategoryUpdate (they continue to use `category_id`).

2. **Transactions (extends Phase 06)**  
   - **TransactionRead**: Expose `subcategory_name` (str) and `hangout_name` (str | null) instead of `subcategory_id` and `hangout_id`.  
   - Service: When returning TransactionRead (list, get, create, update), eager-load `Transaction.subcategory` and `Transaction.hangout` and set `subcategory_name = row.subcategory.name`, `hangout_name = row.hangout.name if row.hangout else None`.  
   - No change to TransactionCreate or TransactionUpdate (they continue to use `subcategory_id`, `hangout_id`).

3. **Schemas**  
   - `app/schemas/subcategory.py`: SubcategoryRead — remove `category_id`, add `category_name: str`.  
   - `app/schemas/transaction.py`: TransactionRead — remove `subcategory_id` and `hangout_id`, add `subcategory_name: str` and `hangout_name: str | None = None`.

4. **Tests**  
   - Unit: `test_services_subcategory.py` — assert `result.category_name` (not `category_id`).  
   - Unit: `test_services_transaction.py` — assert `result.subcategory_name`, `result.hangout_name` (not ids).  
   - Integration: `test_subcategories_api.py` — expect `category_name` in responses; do not expect `category_id`.  
   - Integration: `test_transactions_api.py` — expect `subcategory_name`, `hangout_name` in responses; do not expect `subcategory_id`, `hangout_id`.

---

## Out of scope

- Database or migration changes (IDs remain in DB and in create/update payloads).  
- Changes to Phase 04 (Categories) or Phase 07 (Hangouts) read schemas.

---

## Definition of done (Phase 09)

- [ ] SubcategoryRead has `category_name` (no `category_id`); service builds read DTOs with category name from relationship.  
- [ ] TransactionRead has `subcategory_name` and `hangout_name` (no subcategory_id, hangout_id); service builds read DTOs with names from relationships.  
- [ ] All subcategory and transaction list/get/create/update responses return the new fields; unit and integration tests updated and passing.  
- [ ] Gate passes before every commit: `uv run pytest && uv run robot tests/robot && uv run ruff check .`.
