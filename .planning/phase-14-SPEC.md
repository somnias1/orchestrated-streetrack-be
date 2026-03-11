# Phase 14 — Bulk transactions

## Goal

Add strict normalized-ID bulk transaction creation: validate ownership of all referenced subcategories (and optional hangouts) first, then create all transactions in a single all-or-nothing DB transaction.

## TECHSPEC alignment

- **§1.3:** Bulk transactions: normalized-ID bulk creation validates ownership first and is all-or-nothing.
- **§4.3:** POST `/transactions/bulk` — body: TransactionBulkCreate → 201: TransactionRead[] | 401, 404, 422.

## Scope

### 1. Schema

- **TransactionBulkCreate:** wrapper containing a list of transaction items. Each item has the same normalized-ID shape as single create: `subcategory_id` (UUID, required), `value` (int), `description` (str), `date` (date), `hangout_id` (UUID | null, optional).

### 2. Endpoint

- **POST /transactions/bulk**
  - Auth: required (CurrentUserId).
  - Request body: TransactionBulkCreate.
  - Success: 201 Created, body = TransactionRead[] (created rows in order).
  - Errors: 401 (missing/invalid token), 404 (any subcategory or hangout not found or not owned), 422 (validation error).

### 3. Behavior

- **Ownership check first:** Before creating any row, validate that every `subcategory_id` exists and is owned by the user, and every non-null `hangout_id` exists and is owned by the user. If any check fails, return 404 and create nothing.
- **All-or-nothing:** If all checks pass, create all transactions in a single database transaction; on success commit and return the list of TransactionRead; on any failure roll back (no partial insert).

### 4. Tests

- Unit: service `bulk_create_transactions` — success with multiple items; 404 when a subcategory is not owned; 404 when a hangout is not owned; all-or-nothing (e.g. no rows created when a later item would fail ownership).
- Integration: POST /transactions/bulk — 201 and returned list; 401 without token; 404 when body references subcategory or hangout not owned; 422 on invalid body.
- §1.3 mapping: Bulk transactions row updated with test locations (Phase 14/16).

## Out of scope (this phase)

- Transaction manager import/export (Phase 15); CSV or paste parsing.
- Changes to single-transaction create or list.
