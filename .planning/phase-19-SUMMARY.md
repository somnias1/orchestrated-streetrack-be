# Phase 19 — Transactions list pagination

## What was built

- **`GET /transactions/`** returns **`PaginatedRead[TransactionRead]`**: `items`, `total`, `skip`, `limit`, `has_more`, `next_skip` (same semantics as Phase 17–18 for other lists).
- **`list_transactions`** (`app/services/transaction.py`): shared **`and_(*conditions)`** filter, count query, then paged query with existing **`joinedload`** and **`date.desc()`** order.

## Files changed

- `app/services/transaction.py` — paginated list + `paginated_read`.
- `app/routers/transaction.py` — `PaginatedRead[TransactionRead]` on list route.
- `tests/unit/test_services_transaction.py` — `.items` / `.total`; **`test_list_transactions_pagination_total_skip_and_has_more`**.
- `tests/integration/test_transactions_api.py` — envelope assertions on list responses; bulk test uses **`list_data["items"]`**.
- `tests/robot/smoke.robot` — transaction list length from **`${r.json()}[items]`**.
- `tests/integration/test_openapi_contract.py` — assert **`get`** on **`/transactions/`**.
- `TECHSPEC.md` — §1.3, §4.3 table, pagination subsection title/body, §1.3 mapping row, §8.1 phase row, changelog.
- `STATE.md` — current phase + key decision.
- `.planning/phase-00-ROADMAP.md` — Phase 19 row.

## Decisions made

- **Breaking change** for clients that expected a raw JSON array from `GET /transactions/`; FE should use **`response.items`** (and `total` / hints) like other list endpoints.
- **`total`** respects all active list filters, before **`skip`/`limit`**.

## Tests added / updated

- **`test_list_transactions_pagination_total_skip_and_has_more`** — two-page slice over three rows.
- List-related unit and integration tests updated for envelope shape.

## Known issues / follow-ups

- Robot against **`localhost:8000`** requires a running app; pytest does not.
