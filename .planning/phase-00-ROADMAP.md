# Phase Roadmap

Derived from TECHSPEC.md on 2026-03-06.

| Phase | Name                    | Goal                                                                                   | Key TECHSPEC sections  | Depends on |
| ----- | ----------------------- | -------------------------------------------------------------------------------------- | ---------------------- | ---------- |
| 01    | Foundation              | Project scaffold, deps, tooling, app structure, .gitattributes                          | ?2.1, ?2.2, ?2.3, ?3.2 | ?          |
| 02    | Data model + migrations | ORM models (Category, Subcategory, Transaction, Hangout), Alembic, initial migration   | ?4.1, ?4.2             | 01         |
| 03    | Auth                    | Auth0 JWT validation, get_current_user_id, CurrentUserId                              | ?3.1, ?4.4             | 01         |
| 04    | Categories CRUD         | Router, service, schemas, list/get/create/update/delete                                | ?3.2, ?4.1, ?4.3       | 02, 03     |
| 05    | Subcategories CRUD     | CRUD + category ownership checks                                                       | ?4.1, ?4.3             | 04         |
| 06    | Transactions CRUD      | CRUD + subcategory and optional hangout ownership                                      | ?4.1, ?4.3             | 05         |
| 07    | Hangouts CRUD          | CRUD scoped by user_id                                                                  | ?4.1, ?4.3             | 02, 03     |
| 08    | Tests & verification   | Pytest + Robot, coverage gate, ?1.3 mapping table, DoD                                  | ?1.3, ?6, ?8.3         | 01?07      |
| 09    | Read responses: names not IDs | SubcategoryRead returns category_name; TransactionRead returns subcategory_name, hangout_name | ?4.1, ?4.3             | 05, 06, 08 |

## Phase sizing guidance

- Each phase targets **one chat session** worth of work.
- If a phase feels too large (>8 atomic commits), split it.
- If two phases are very small (<2 commits each), consider merging them.
- New features after initial build continue from Phase 09+ (see FRAMEWORK.md ?6).
