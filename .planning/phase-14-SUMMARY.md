# Phase 14 — Bulk transactions

## What was built

- **TransactionBulkCreate** schema: wrapper with `transactions: list[TransactionCreate]` for normalized-ID bulk payload.
- **POST /transactions/bulk** endpoint: auth required; body `TransactionBulkCreate`; 201 with `TransactionRead[]`; 401/404/422 per §4.3.
- **bulk_create_transactions** service: validate ownership of every subcategory and optional hangout first; if any fails → 404 and no rows created; otherwise create all in one commit (all-or-nothing).

## Files changed

- `.planning/phase-14-SPEC.md`: added (phase spec).
- `app/schemas/transaction.py`: added `TransactionBulkCreate`.
- `app/services/transaction.py`: added `bulk_create_transactions`; reuse `_ensure_subcategory_owned` / `_ensure_hangout_owned`.
- `app/routers/transaction.py`: added `POST /bulk` route (before `/{transaction_id}`).
- `tests/unit/test_services_transaction.py`: added 4 tests (success, 404 subcategory, 404 hangout, all-or-nothing).
- `tests/integration/test_transactions_api.py`: added 4 tests (201 + list, 401, 404 not owned, 422 invalid body).
- `TECHSPEC.md`: §1.3 test mapping updated for bulk transactions.

## Decisions made

- Bulk body shape: single field `transactions` (list of same shape as single create) to keep OpenAPI clear and allow future constraints (e.g. max length) on the list.
- Ownership validated up front for all items before any insert, so 404 implies no partial create (all-or-nothing).

## Tests added

- `tests/unit/test_services_transaction.py`: `test_bulk_create_transactions_success`, `test_bulk_create_transactions_404_when_subcategory_not_owned`, `test_bulk_create_transactions_404_when_hangout_not_owned`, `test_bulk_create_transactions_all_or_nothing`.
- `tests/integration/test_transactions_api.py`: `test_bulk_create_transactions_201_and_returns_list`, `test_bulk_create_transactions_without_auth_returns_401`, `test_bulk_create_transactions_404_when_subcategory_not_owned`, `test_bulk_create_transactions_invalid_body_422`.

## §1.3 case verification

| §1.3 case | Test location |
|-----------|----------------|
| Bulk transactions: normalized-ID batch, ownership check, all-or-nothing | tests/unit/test_services_transaction.py (test_bulk_create_transactions_*), tests/integration/test_transactions_api.py (test_bulk_create_transactions_*) |

## Known issues / follow-ups

- None.
