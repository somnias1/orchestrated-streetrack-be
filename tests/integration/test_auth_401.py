"""
Integration tests: 401 when no auth on protected endpoints. §1.3 Auth: missing token → 401.
"""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_list_categories_without_auth_returns_401(client: TestClient) -> None:
    """GET /categories/ without X-Test-User-Id returns 401."""
    r = client.get("/categories/")
    assert r.status_code == 401


def test_post_categories_without_auth_returns_401(client: TestClient) -> None:
    """POST /categories/ without auth returns 401."""
    r = client.post("/categories/", json={"name": "Food", "description": None, "is_income": False})
    assert r.status_code == 401


def test_validation_error_returns_422_detail(client: TestClient) -> None:
    """§1.3 API contract: 422 on validation errors with detail: ValidationError[]."""
    # Missing required field "name" for CategoryCreate
    r = client.post(
        "/categories/",
        headers={"X-Test-User-Id": "user-1"},
        json={"description": "No name", "is_income": False},
    )
    assert r.status_code == 422
    data = r.json()
    assert "detail" in data
    assert isinstance(data["detail"], list)
    assert len(data["detail"]) >= 1
    item = data["detail"][0]
    assert "loc" in item and "msg" in item and "type" in item
