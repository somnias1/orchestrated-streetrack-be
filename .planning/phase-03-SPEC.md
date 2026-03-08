# Phase 03 — Auth

**Goal (ROADMAP):** Auth0 JWT validation, get_current_user_id, CurrentUserId.

**Key TECHSPEC:** §3.1 (High-level architecture — request flow, auth), §4.4 (Authentication).

---

## Scope

### 1. Auth0 JWT validation (§4.4)

- **Mechanism:** Auth0 JWT (OAuth2/OIDC). Validate using **JWKS** from Auth0 domain; extract **`sub`** as `user_id`.
- **Config:** Use existing `Settings`: `auth0_domain`, `auth0_audience`, `auth0_issuer`. Empty domain = auth disabled (e.g. local dev); see §2 below.
- **Dependencies:** `python-jose[cryptography]` and `requests` already in pyproject.toml; use for JWKS fetch and JWT verify.

### 2. get_current_user_id dependency (§3.1, §4.4)

- **Signature:** FastAPI dependency that returns `str` (the `sub` claim) or raises **HTTPException 401** when:
  - Authorization header is missing or not Bearer
  - Token is invalid, malformed, or expired
  - JWKS fetch or verification fails
- **CurrentUserId:** Type alias for the dependency return type (e.g. `str`) so routers can declare `user_id: CurrentUserId = Depends(get_current_user_id)` in later phases.
- **Optional auth (local dev):** If `AUTH0_DOMAIN` is empty, `get_current_user_id` may either (a) raise 401 on any protected route, or (b) accept a well-known dev token / skip validation and return a fixed dev user id. Spec prefers (a) for simplicity: when domain is empty, require no token and reject with 401 for “protected” routes, OR document that protected routes are not mounted until domain is set. **Decision:** When `auth0_domain` is empty, `get_current_user_id` raises 401 (no bypass). This keeps behavior consistent; local dev can use a real Auth0 tenant or mock at the test layer.

### 3. Request flow (§3.1)

- Bearer token → **get_current_user_id** → (later) router → service. This phase only adds the auth module and dependency; no routers use it yet (Phase 04+).
- **Unsecured routes:** GET `/`, GET `/health` remain public (no dependency).

### 4. Out of scope this phase

- Mounting `get_current_user_id` on resource routers (Categories, etc.) — Phase 04+.
- Roles/scopes — not in v1.

---

## Tasks (atomic commits)

1. **feat(03): add phase-03 spec** — this spec committed on the phase branch.
2. **feat(03): implement Auth0 JWKS fetch and JWT validation in app/auth.py** — JWKS URL from settings, fetch and cache (in-memory or per-request), verify token (signature, audience, issuer, expiry), extract `sub`; define `get_current_user_id` and `CurrentUserId`.
3. **test(03): add unit tests for get_current_user_id** — valid token → user_id; invalid token → 401; missing token → 401. Mock JWKS/jose so tests do not call Auth0.

---

## Definition of Done (Phase 03)

- [ ] Spec committed before implementation code.
- [ ] `app/auth.py` exports `get_current_user_id`, `CurrentUserId`; validates JWT via Auth0 JWKS; returns `sub` or 401.
- [ ] Unit tests: valid token → user_id; invalid/missing token → 401.
- [ ] Gate passes: `uv run pytest && uv run robot tests/robot && uv run ruff check .`
