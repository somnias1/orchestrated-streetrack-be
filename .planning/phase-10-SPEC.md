# Phase 10 — Finance expansion spec refresh

## Scope

**Documentation only.** No application code changes.

Align TECHSPEC, BACKLOG, STATE.md, and `.planning/phase-00-ROADMAP.md` with the finance expansion stream (phases 11–16) so that:

- **§1.2 Goals** and **§1.3 Success Criteria** clearly cover filters, periodic expenses, dashboard, bulk transactions, and import/export.
- **§1.3 Test coverage mapping** includes rows (or placeholders) for the new finance cases so Phase 16 can fill them.
- **§4.1 Data model** and **§4.3 APIs & Contracts** are the single source of truth for phases 11–15.
- **BACKLOG.md** High-priority backend items (10–16) and wording match the roadmap.
- **STATE.md** and **ROADMAP** stay consistent with TECHSPEC and BACKLOG.

## Deliverables

1. **TECHSPEC.md** — Review and update §1.2, §1.3, §4.1, §4.3 for consistency with phases 11–16; add §1.3 mapping rows for finance expansion cases.
2. **BACKLOG.md** — Ensure Phase 10–16 items and backend/frontend alignment text are correct.
3. **STATE.md** — After phase: set current phase to "Phase 10 — Complete", next task to Phase 11.
4. **.planning/phase-00-ROADMAP.md** — Confirm Phase 10 and 11–16 rows match TECHSPEC and BACKLOG; adjust if needed.
5. **.planning/phase-10-SUMMARY.md** — Created at phase end (what was updated, decisions, no code changes).

## Out of scope

- Any changes under `app/` or `tests/` (no new code, no new tests).
- Implementation of filters, periodic expenses, dashboard, bulk, or import/export (those are phases 11–16).

## Definition of done

- All four doc artifacts updated and committed.
- Gate `uv run pytest && uv run robot tests/robot && uv run ruff check .` passes before every commit (no app change, so unchanged).
- Phase branch merged to `main` with `--no-ff` after SUMMARY and STATE update.
