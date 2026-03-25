# Phase Roadmap

Derived from TECHSPEC.md on 2026-03-09.

| Phase | Name | Goal | Key TECHSPEC sections | Depends on |
| ----- | ---- | ---- | --------------------- | ---------- |
| 01 | Foundation | Project scaffold, deps, tooling, app structure, .gitattributes | Sec 2.1, Sec 2.2, Sec 2.3, Sec 3.2 | - |
| 02 | Data model + migrations | ORM models (Category, Subcategory, Transaction, Hangout), Alembic, initial migration | Sec 4.1, Sec 4.2 | 01 |
| 03 | Auth | Auth0 JWT validation, get_current_user_id, CurrentUserId | Sec 3.1, Sec 4.4 | 01 |
| 04 | Categories CRUD | Router, service, schemas, list/get/create/update/delete | Sec 3.2, Sec 4.1, Sec 4.3 | 02, 03 |
| 05 | Subcategories CRUD | CRUD + category ownership checks | Sec 4.1, Sec 4.3 | 04 |
| 06 | Transactions CRUD | CRUD + subcategory and optional hangout ownership | Sec 4.1, Sec 4.3 | 05 |
| 07 | Hangouts CRUD | CRUD scoped by user_id | Sec 4.1, Sec 4.3 | 02, 03 |
| 08 | Tests & verification | Pytest + Robot, coverage gate, Sec 1.3 mapping table, DoD | Sec 1.3, Sec 6, Sec 8.3 | 01-07 |
| 09 | Read responses: names not IDs | SubcategoryRead returns category_name; TransactionRead returns subcategory_name and hangout_name | Sec 4.1, Sec 4.3 | 05, 06, 08 |
| 10 | Finance expansion spec refresh | Update TECHSPEC, BACKLOG, STATE, and roadmap for filters, periodic expenses, dashboard, bulk transactions, and import/export | Sec 1.2, Sec 1.3, Sec 4.1, Sec 4.3 | 09 |
| 11 | Filtering and sorting foundation | Add list filters for categories, subcategories, and transactions while keeping current response envelopes | Sec 1.3, Sec 4.3 | 10 |
| 12 | Periodic expenses | Add subcategory periodic-expense fields, validation, and due-status business rules | Sec 1.3, Sec 4.1, Sec 4.3 | 10, 11 |
| 13 | Home dashboard read APIs | Add separate endpoints for cumulative balance, selected-month balance, and due periodic expenses | Sec 1.3, Sec 3.6, Sec 4.3 | 11, 12 |
| 14 | Bulk transactions | Add strict normalized-ID bulk transaction creation | Sec 1.3, Sec 4.3 | 11 |
| 15 | Transaction manager import/export | Add import preview/validation and CSV export flows on top of stable filters and bulk create | Sec 1.3, Sec 4.3 | 11, 14 |
| 16 | Finance expansion tests & handoff | Add tests, robot coverage where practical, and FE contract verification for the new finance APIs | Sec 1.3, Sec 6, Sec 8.3 | 11-15 |
| 17 | Name filters + pagination envelope | Add name `icontains` filters on categories/subcategories/hangouts list endpoints and return a pagination envelope (`items`, `total`, `skip`, `limit`) | Sec 1.3, Sec 4.3 | 11, 16 |
| 18 | Pagination convenience fields | Add server-side next-page hints (`has_more`, `next_skip`) so FE can avoid client-side calculations for enabling “next page” actions | Sec 1.3, Sec 4.3 | 17 |
| 19 | Transactions list pagination | Align `GET /transactions/` with the same `PaginatedRead` envelope as other list APIs (`items`, `total`, `skip`, `limit`, `has_more`, `next_skip`); preserve filters and newest-first sort | Sec 1.3, Sec 4.3 | 18 |

**Note:** Phase 10 is documentation only (no application code).

## Phase sizing guidance

- Each phase targets **one chat session** worth of work.
- If a phase feels too large (>8 atomic commits), split it.
- If two phases are very small (<2 commits each), consider merging them.
- New features after initial build continue from the next roadmap phase number (see `FRAMEWORK.md` Sec 6).
