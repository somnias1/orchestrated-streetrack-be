"""
Auth0 JWT validation and get_current_user_id dependency.
Per TECHSPEC §3.1, §4.4.
"""

from __future__ import annotations

import time
from typing import Annotated

import requests
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.db.config import Settings

# Registers `Bearer` in OpenAPI so Swagger UI shows Authorize; does not auto-401 when missing.
bearer_scheme = HTTPBearer(auto_error=False)


def _get_settings() -> Settings:
    return Settings()


# In-memory JWKS cache: domain -> (jwks_dict, expiry_timestamp). TTL 300s.
_jwks_cache: dict[str, tuple[dict, float]] = {}
JWKS_CACHE_TTL = 300


def _fetch_jwks(domain: str) -> dict:
    """Fetch JWKS from Auth0 domain. Cached for JWKS_CACHE_TTL seconds."""
    now = time.monotonic()
    if domain in _jwks_cache:
        cached, expiry = _jwks_cache[domain]
        if now < expiry:
            return cached
    url = f"https://{domain.rstrip('/')}/.well-known/jwks.json"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        jwks = resp.json()
    except (requests.RequestException, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWKS unavailable",
        ) from e
    _jwks_cache[domain] = (jwks, now + JWKS_CACHE_TTL)
    return jwks


def _get_signing_key(jwks: dict, kid: str | None) -> dict | None:
    """Return the JWK with the given kid, or None."""
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    return None


def _get_bearer_token(authorization: str | None) -> str | None:
    if not authorization or not authorization.strip().lower().startswith("bearer "):
        return None
    return authorization.strip()[7:].strip()  # after "Bearer "


def get_current_user_id_impl(
    authorization: str | None,
    settings: Settings,
) -> str:
    """
    Core logic: validate Bearer token and return sub.
    Used by dependency that injects Authorization from Request.
    """
    if not settings.auth0_domain or not settings.auth0_domain.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication not configured",
        )

    token = _get_bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode header without verification to get kid
    try:
        header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    kid = header.get("kid")
    jwks = _fetch_jwks(settings.auth0_domain)
    signing_key = _get_signing_key(jwks, kid)
    if not signing_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=settings.auth0_audience or None,
            issuer=settings.auth0_issuer or None,
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return str(sub)


def get_current_user_id(
    request: Request,
    settings: Annotated[Settings, Depends(_get_settings)],
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ],
) -> str:
    """
    FastAPI dependency: validate Bearer JWT via Auth0 JWKS and return `sub` as user_id.
    Raises 401 when AUTH0_DOMAIN is unset, or when token is missing/invalid/expired.
    """
    if credentials is not None:
        authorization = f"Bearer {credentials.credentials}"
    else:
        authorization = request.headers.get("Authorization")
    return get_current_user_id_impl(authorization, settings)


# Type alias for use in routers (e.g. user_id: CurrentUserId = Depends(get_current_user_id))
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
