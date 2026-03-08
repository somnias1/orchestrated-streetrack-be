"""
Unit tests for get_current_user_id / get_current_user_id_impl.
§1.3: Auth valid token → user_id; invalid token → 401; missing token → 401.
"""

from __future__ import annotations

import base64
from unittest.mock import patch

import pytest
from app.auth import get_current_user_id_impl
from app.db.config import Settings
from fastapi import HTTPException


def _jwk_from_rsa_public(public_key: object, kid: str = "test") -> dict:
    """Build JWK dict from cryptography RSAPublicKey (n, e base64url)."""
    from cryptography.hazmat.primitives.asymmetric import rsa

    pub = public_key
    if not isinstance(pub, rsa.RSAPublicKey):
        raise TypeError("expected RSAPublicKey")
    n = pub.public_numbers().n
    e = pub.public_numbers().e

    def b64url(b: bytes) -> str:
        return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")

    n_b = n.to_bytes((n.bit_length() + 7) // 8, "big")
    e_b = e.to_bytes((e.bit_length() + 7) // 8, "big")
    return {"kty": "RSA", "kid": kid, "alg": "RS256", "n": b64url(n_b), "e": b64url(e_b)}


@pytest.fixture
def rsa_key_and_jwks():
    """Generate RSA key pair and JWKS for testing. No network."""
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        NoEncryption,
        PrivateFormat,
    )

    key = rsa.generate_private_key(65537, 2048, default_backend())
    public_jwk = _jwk_from_rsa_public(key.public_key(), kid="test")
    pem = key.private_bytes(Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption())
    jwks = {"keys": [public_jwk]}
    return {"private_pem": pem, "jwks": jwks, "public_jwk": public_jwk}


@pytest.fixture
def settings_with_auth():
    """Settings with Auth0 configured (no real calls when _fetch_jwks is mocked)."""
    return Settings(
        auth0_domain="test.auth0.com",
        auth0_audience="https://api.test",
        auth0_issuer="https://test.auth0.com/",
    )


def test_valid_token_returns_user_id(rsa_key_and_jwks, settings_with_auth) -> None:
    """Valid token yields user_id (sub). §1.3 Auth: valid token → user_id."""
    from jose import jwt

    pem = rsa_key_and_jwks["private_pem"]
    jwks = rsa_key_and_jwks["jwks"]
    claims = {
        "sub": "auth0|user-123",
        "aud": settings_with_auth.auth0_audience,
        "iss": settings_with_auth.auth0_issuer,
        "exp": 9999999999,
        "iat": 0,
    }
    token = jwt.encode(claims, pem, algorithm="RS256", headers={"kid": "test"})
    auth_header = f"Bearer {token}"

    with patch("app.auth._fetch_jwks", return_value=jwks):
        result = get_current_user_id_impl(auth_header, settings_with_auth)
    assert result == "auth0|user-123"


def test_missing_token_raises_401(settings_with_auth) -> None:
    """Missing or non-Bearer Authorization yields 401. §1.3 Auth: missing token → 401."""
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id_impl(None, settings_with_auth)
    assert exc_info.value.status_code == 401

    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id_impl("", settings_with_auth)
    assert exc_info.value.status_code == 401

    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id_impl("Basic abc", settings_with_auth)
    assert exc_info.value.status_code == 401


def test_invalid_token_raises_401(rsa_key_and_jwks, settings_with_auth) -> None:
    """Invalid or wrong-signature token yields 401. §1.3 Auth: invalid token → 401."""
    jwks = rsa_key_and_jwks["jwks"]
    # Token signed with wrong key: use a different key to sign, JWKS has the first key
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        NoEncryption,
        PrivateFormat,
    )
    from jose import jwt

    other_key = rsa.generate_private_key(65537, 2048, default_backend())
    other_pem = other_key.private_bytes(
        Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption()
    )
    claims = {
        "sub": "user-bad",
        "aud": settings_with_auth.auth0_audience,
        "iss": settings_with_auth.auth0_issuer,
        "exp": 9999999999,
        "iat": 0,
    }
    token = jwt.encode(claims, other_pem, algorithm="RS256", headers={"kid": "test"})
    auth_header = f"Bearer {token}"

    with patch("app.auth._fetch_jwks", return_value=jwks):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user_id_impl(auth_header, settings_with_auth)
    assert exc_info.value.status_code == 401


def test_auth_not_configured_raises_401() -> None:
    """Empty AUTH0_DOMAIN yields 401 (auth not configured)."""
    empty_settings = Settings(auth0_domain="", auth0_audience="", auth0_issuer="")
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id_impl("Bearer any", empty_settings)
    assert exc_info.value.status_code == 401
