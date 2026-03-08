"""
Integration: Categories API — one full flow. §1.3 CRUD scoped; 404 when not owned.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-Test-User-Id": "test-user-categories"}


def test_categories_flow(client: TestClient, clean_db: None, auth_headers: dict[str, str]) -> None:
    """List (empty) → create → list (one) → get → update → get → delete → get 404."""
    # List empty
    r = client.get("/categories/", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []

    # Create
    r = client.post(
        "/categories/",
        headers=auth_headers,
        json={"name": "Food", "description": "Meals", "is_income": False},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Food"
    assert data["description"] == "Meals"
    cat_id = data["id"]

    # List returns one
    r = client.get("/categories/", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["id"] == cat_id

    # Get by id
    r = client.get(f"/categories/{cat_id}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Food"

    # Update
    r = client.patch(
        f"/categories/{cat_id}",
        headers=auth_headers,
        json={"name": "Food & Drinks", "description": "Updated"},
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Food & Drinks"

    # Delete
    r = client.delete(f"/categories/{cat_id}", headers=auth_headers)
    assert r.status_code == 204

    # Get returns 404
    r = client.get(f"/categories/{cat_id}", headers=auth_headers)
    assert r.status_code == 404


def test_categories_get_404_when_not_owned(
    client: TestClient, clean_db: None, auth_headers: dict[str, str]
) -> None:
    """GET /categories/{id} returns 404 when resource belongs to another user."""
    # User A creates category
    r = client.post(
        "/categories/",
        headers={"X-Test-User-Id": "user-a"},
        json={"name": "Secret", "description": None, "is_income": False},
    )
    assert r.status_code == 201
    cat_id = r.json()["id"]

    # User B tries to get it
    r = client.get(f"/categories/{cat_id}", headers={"X-Test-User-Id": "user-b"})
    assert r.status_code == 404
