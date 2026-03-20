"""
Integration: Subcategories API — one full flow. §1.3 CRUD + category ownership; 404 when not owned.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def category_id(client: TestClient, clean_db: None) -> str:
    """Create a category and return its id (user test-user-sub)."""
    r = client.post(
        "/categories/",
        headers={"X-Test-User-Id": "test-user-sub"},
        json={"name": "Parent", "description": None, "is_income": False},
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_subcategories_flow(client: TestClient, clean_db: None, category_id: str) -> None:
    """List → create → list → get → update → delete. Category owned by same user."""
    headers = {"X-Test-User-Id": "test-user-sub"}

    r = client.get("/subcategories/", headers=headers)
    assert r.status_code == 200
    empty = r.json()
    assert empty["items"] == []
    assert empty["total"] == 0
    assert empty["has_more"] is False
    assert empty["next_skip"] is None

    r = client.post(
        "/subcategories/",
        headers=headers,
        json={
            "category_id": category_id,
            "name": "Lunch",
            "description": None,
            "belongs_to_income": False,
        },
    )
    assert r.status_code == 201
    data = r.json()
    sub_id = data["id"]
    assert data["category_id"] == category_id
    assert data["category_name"] == "Parent"

    r = client.get("/subcategories/", headers=headers)
    assert r.status_code == 200
    listed = r.json()
    assert len(listed["items"]) == 1
    assert listed["total"] == 1
    assert listed["has_more"] is False
    assert listed["next_skip"] is None

    r = client.get(f"/subcategories/{sub_id}", headers=headers)
    assert r.status_code == 200
    get_data = r.json()
    assert get_data["name"] == "Lunch"
    assert get_data["category_id"] == category_id
    assert get_data["category_name"] == "Parent"

    r = client.patch(
        f"/subcategories/{sub_id}",
        headers=headers,
        json={"name": "Lunch & Coffee"},
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Lunch & Coffee"

    r = client.delete(f"/subcategories/{sub_id}", headers=headers)
    assert r.status_code == 204

    r = client.get(f"/subcategories/{sub_id}", headers=headers)
    assert r.status_code == 404


def test_subcategories_get_404_when_not_owned(
    client: TestClient, clean_db: None, category_id: str
) -> None:
    """GET /subcategories/{id} returns 404 when subcategory belongs to another user."""
    r = client.post(
        "/subcategories/",
        headers={"X-Test-User-Id": "user-a"},
        json={
            "category_id": category_id,
            "name": "Mine",
            "description": None,
            "belongs_to_income": False,
        },
    )
    # category was created by test-user-sub, so POST as user-a will 404 (category not owned)
    # So we need a category owned by user-a first
    r = client.post(
        "/categories/",
        headers={"X-Test-User-Id": "user-a"},
        json={"name": "CatA", "description": None, "is_income": False},
    )
    assert r.status_code == 201
    cat_a_id = r.json()["id"]
    r = client.post(
        "/subcategories/",
        headers={"X-Test-User-Id": "user-a"},
        json={
            "category_id": cat_a_id,
            "name": "SubA",
            "description": None,
            "belongs_to_income": False,
        },
    )
    assert r.status_code == 201
    sub_id = r.json()["id"]

    r = client.get(f"/subcategories/{sub_id}", headers={"X-Test-User-Id": "user-b"})
    assert r.status_code == 404
