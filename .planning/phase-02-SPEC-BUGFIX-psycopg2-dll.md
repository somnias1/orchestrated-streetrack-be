# Phase 02 — Bugfix: psycopg2 DLL load failure

**Branch:** `feature/phase-02-bugfix-psycopg2-dll`

---

## Bug

- **Observed:** On some environments (e.g. Windows), `alembic upgrade head` and the app fail with:
  `ImportError: DLL load failed while importing _psycopg: No se puede encontrar el módulo especificado.`
- **Expected:** `alembic upgrade head` and the app run successfully when `DATABASE_URL` is set and PostgreSQL is available.

## Root cause

The pinned dependency `psycopg2-binary==2.9.10` can install a wheel that is incompatible with the current Python/runtime (e.g. missing or mismatched VC++ runtime), so the native `_psycopg` extension fails to load.

## Fix approach

1. Relax `psycopg2-binary` in `pyproject.toml` to `>=2.9.10` so the resolver can pick a compatible wheel (e.g. a newer build that works on the target environment). Minimum 2.9.x kept for consistency with the original pin.
2. Re-run `uv lock` to update `uv.lock`.
3. Document the decision in `.planning/phase-02-SUMMARY.md` (Decisions made + Files changed) and in `STATE.md` (Key Decisions) per FRAMEWORK.

## Definition of Done

- [ ] SPEC committed before implementation.
- [ ] `pyproject.toml` and `uv.lock` updated; phase-02-SUMMARY and STATE updated.
- [ ] Gate passes: `uv run pytest && uv run robot tests/robot && uv run ruff check .`
- [ ] Merge to `main` with `--no-ff`.
