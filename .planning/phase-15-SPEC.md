# Phase 15 — Transaction manager import/export

## Goal (from ROADMAP)

Add import preview/validation and CSV export flows on top of stable filters and bulk create.

## TECHSPEC scope

- **§1.3:** Import validates pasted sheet rows against existing category/subcategory pairs and returns a payload ready for bulk creation; export returns date-filtered CSV ordered oldest to newest.
- **§4.3:** Contract table:
  - **POST** `/transaction-manager/import` — body: `TransactionImportRequest` → 200: `TransactionImportPreview` (401, 404, 422).
  - **GET** `/transaction-manager/export` — query: `year?`, `month?`, `day?`, `subcategory_id?`, `hangout_id?` → 200: `text/csv` (401, 422).

## Out of scope

- Phase 16 test handoff (mapping table update for import/export will be noted in Phase 15 summary; full §1.3 mapping in Phase 16).

---

## 1. Import

### 1.1 Request: `TransactionImportRequest`

- **Schema:** One row per pasted sheet line; each row identified by category + subcategory **names** (user’s existing pairs only).
- **Fields per row (e.g. `TransactionImportRow`):**
  - `category_name: str`
  - `subcategory_name: str`
  - `value: int`
  - `description: str`
  - `date: date`
  - `hangout_id: uuid | None` (optional; must be owned by user if present)
- **Body:** `TransactionImportRequest` with `rows: list[TransactionImportRow]`.

### 1.2 Validation rules

- Resolve each row’s `(category_name, subcategory_name)` against the **current user’s** categories and subcategories only.
- If the pair exists and is owned: resolve to `subcategory_id`; optionally validate `hangout_id` belongs to user; produce a normalized `TransactionCreate` (subcategory_id, value, description, date, hangout_id).
- If the pair does not exist or is not owned: record a validation error for that row (e.g. row index + message); do **not** include it in the payload ready for bulk create.
- No 404 for “no rows”: return 200 with preview; preview may have empty `transactions` and non-empty `invalid_rows`.

### 1.3 Response: `TransactionImportPreview`

- **Payload ready for bulk create:** `transactions: list[TransactionCreate]` — only rows that resolved to a valid (subcategory_id, optional hangout_id) for the user.
- **Validation feedback:** `invalid_rows: list[TransactionImportInvalidRow]` with at least `row_index: int`, `message: str` (e.g. “Category/subcategory pair not found or not owned”).
- Frontend can then call **POST** `/transactions/bulk` with `TransactionBulkCreate(transactions=preview.transactions)`.

---

## 2. Export

### 2.1 Endpoint

- **GET** `/transaction-manager/export`
- **Query params:** Same as transaction list filters: `year?`, `month?`, `day?`, `subcategory_id?`, `hangout_id?` (all optional). No skip/limit; export returns all matching rows (or we cap with a reasonable limit if needed; TECHSPEC says “date-filtered CSV” so same filters as list).
- **Response:** `200`, `Content-Type: text/csv`.
- **Order:** Oldest to newest (ascending date), per §1.3.

### 2.2 CSV format

- Header row: e.g. `date,subcategory_id,subcategory_name,value,description,hangout_id,hangout_name` (or similar; enough for FE/backup).
- One row per transaction; columns consistent with TransactionRead (date, subcategory_id, subcategory_name, value, description, hangout_id, hangout_name).
- User-scoped: only the authenticated user’s transactions.

---

## 3. Implementation tasks

1. **Schemas:** Add `TransactionImportRow`, `TransactionImportRequest`, `TransactionImportInvalidRow`, `TransactionImportPreview` (e.g. in `app/schemas/transaction.py` or a dedicated `app/schemas/transaction_manager.py`).
2. **Service:** Add `preview_import(db, user_id, request) -> TransactionImportPreview` (resolve rows, build list of TransactionCreate + list of invalid rows). Add `export_transactions_csv(db, user_id, year?, month?, day?, subcategory_id?, hangout_id?)` returning CSV bytes or string.
3. **Router:** New router `app/routers/transaction_manager.py` with prefix `/transaction-manager`, tags `["transaction-manager"]`; POST `/import`, GET `/export`; both protected with `CurrentUserId` and `get_db`.
4. **Main:** Include transaction_manager router in `app/main.py`.
5. **Tests:** Unit tests for preview_import (resolve ok, resolve missing pair, hangout ownership); unit tests for export (filters, order oldest first); integration tests for POST `/transaction-manager/import` and GET `/transaction-manager/export` (auth, 200, CSV shape).

---

## 4. Definition of Done (Phase 15)

- [ ] `.planning/phase-15-SPEC.md` committed before implementation.
- [ ] POST `/transaction-manager/import` and GET `/transaction-manager/export` implemented per §4.3.
- [ ] Import resolves only existing category/subcategory pairs for the user; preview returns normalized transactions + invalid_rows.
- [ ] Export returns date-filtered CSV, oldest to newest, with same query filters as transaction list.
- [ ] Gate `uv run pytest && uv run robot tests/robot && uv run ruff check .` passes before every commit.
- [ ] Phase summary and STATE update before merge.
