# Phase 09 — Read responses: names not IDs (Spec)

**Goal:** SubcategoryRead returns category_name; TransactionRead returns subcategory_name and hangout_name (instead of IDs in read responses).  
**Key TECHSPEC:** §4.1 (schema contracts), §4.3 (APIs & contracts).  
**Depends on:** Phase 05 (Subcategories CRUD), Phase 06 (Transactions CRUD), Phase 08 (Tests).

---

## Scope

This phase extends the **read** (response) contracts of Phase 05 and Phase 06. Create/Update request bodies keep using IDs; only the read schemas and the way responses are built change.

1. **Subcategories (extends Phase 05)**  
   - **SubcategoryRead**: Expose `category_id` (uuid) and `category_name` (str). FE uses id for lookups in parent list.  
   - Service: When returning SubcategoryRead (list, get, create, update), eager-load `Subcategory.category` and set `category_id = row.category_id`, `category_name = row.category.name`.  
   - No change to SubcategoryCreate or SubcategoryUpdate (they continue to use `category_id`).

2. **Transactions (extends Phase 06)**  
   - **TransactionRead**: Expose `subcategory_id`, `subcategory_name` (str), `hangout_id` (uuid | null), `hangout_name` (str | null). FE uses ids for lookups.  
   - Service: When returning TransactionRead (list, get, create, update), eager-load `Transaction.subcategory` and `Transaction.hangout` and set ids + names from row/relationships.  
   - No change to TransactionCreate or TransactionUpdate (they continue to use `subcategory_id`, `hangout_id`).

3. **Schemas**  
   - `app/schemas/subcategory.py`: SubcategoryRead — `category_id` (uuid), `category_name` (str).  
   - `app/schemas/transaction.py`: TransactionRead — `subcategory_id`, `subcategory_name`, `hangout_id`, `hangout_name`.

4. **Tests**  
   - Unit and integration: assert/expect both ids and names in read responses.

---

## Out of scope

- Database or migration changes (IDs remain in DB and in create/update payloads).  
- Changes to Phase 04 (Categories) or Phase 07 (Hangouts) read schemas.

---

## Definition of done (Phase 09)

- [x] SubcategoryRead has `category_id` and `category_name`; service builds read DTOs from row + relationship.  
- [x] TransactionRead has `subcategory_id`, `subcategory_name`, `hangout_id`, `hangout_name`; service builds read DTOs from row + relationships.  
- [x] All subcategory and transaction list/get/create/update responses return ids and names; unit and integration tests updated and passing.  
- [x] Gate passes before every commit: `uv run pytest && uv run robot tests/robot && uv run ruff check .`.
