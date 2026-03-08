# Phase 03 — Auth

## What was built

- **Auth0 JWT validation** (TECHSPEC §3.1, §4.4): `app/auth.py` fetches JWKS from `https://{AUTH0_DOMAIN}/.well-known/jwks.json`, caches it in-memory (TTL 300s), and verifies Bearer tokens (signature, audience, issuer, expiry) using `python-jose` and `requests`.
- **get_current_user_id**: FastAPI dependency that reads `Authorization`, validates the JWT, and returns the `sub` claim as `str`; raises **401** when `AUTH0_DOMAIN` is unset, or when the token is missing, invalid, or expired.
- **CurrentUserId**: Type alias `Annotated[str, Depends(get_current_user_id)]` for use in routers (Phase 04+).
- **Optional auth**: When `AUTH0_DOMAIN` is empty, `get_current_user_id_impl` raises 401 with detail "Authentication not configured" (no bypass for local dev; tests mock JWKS).

## Files changed

- `.planning/phase-03-SPEC.md`: Phase scope and tasks.
- `app/auth.py`: Replaced stub with full implementation: `_fetch_jwks`, `_get_signing_key`, `_get_bearer_token`, `get_current_user_id_impl`, `get_current_user_id` (dependency), `CurrentUserId`.
- `tests/unit/test_auth.py`: New unit tests for valid token → user_id, missing token → 401, invalid token → 401, auth not configured → 401 (§1.3 mapping).

## Decisions made

- **No auth bypass**: Empty `AUTH0_DOMAIN` yields 401 on any call to `get_current_user_id`; local dev uses a real Auth0 tenant or mocks at the test layer.
- **JWKS cache**: In-memory cache keyed by domain with 300s TTL to avoid fetching on every request; no invalidation on failure (next request will refetch).
- **Dependency signature**: `get_current_user_id(request: Request, settings: Depends(_get_settings))` so the dependency can read `Authorization`; core logic in `get_current_user_id_impl` for easy unit testing without FastAPI request context.

## Tests added

- `tests/unit/test_auth.py`: `test_valid_token_returns_user_id` (valid RS256 token + mocked JWKS → returns sub), `test_missing_token_raises_401`, `test_invalid_token_raises_401` (wrong key signature), `test_auth_not_configured_raises_401`. JWKS and signing keys generated in tests with `cryptography`; no Auth0 network calls.

## Known issues / follow-ups

- None. Routers do not use `CurrentUserId` yet; Phase 04 will mount `Depends(get_current_user_id)` on category (and later) endpoints.
