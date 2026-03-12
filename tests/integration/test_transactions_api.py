"""
Integration: Transactions API — one full flow. §1.3 CRUD + subcategory/hangout; 404 when not owned.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def subcategory_id(client: TestClient, clean_db: None) -> str:
    """Create category + subcategory for test-user-tx, return subcategory id."""
    r = client.post(
        "/categories/",
        headers={"X-Test-User-Id": "test-user-tx"},
        json={"name": "Cat", "description": None, "is_income": False},
    )
    assert r.status_code == 201
    cat_id = r.json()["id"]
    r = client.post(
        "/subcategories/",
        headers={"X-Test-User-Id": "test-user-tx"},
        json={
            "category_id": cat_id,
            "name": "Sub",
            "description": None,
            "belongs_to_income": False,
        },
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_transactions_flow(
    client: TestClient, clean_db: None, subcategory_id: str
) -> None:
    """List → create → list → get → update → delete."""
    headers = {"X-Test-User-Id": "test-user-tx"}

    r = client.get("/transactions/", headers=headers)
    assert r.status_code == 200
    initial_list = r.json()
    assert isinstance(initial_list, list)

    r = client.post(
        "/transactions/",
        headers=headers,
        json={
            "subcategory_id": subcategory_id,
            "value": -1000,
            "description": "Coffee",
            "date": "2025-03-01",
            "hangout_id": None,
        },
    )
    assert r.status_code == 201
    data = r.json()
    tx_id = data["id"]
    assert data["subcategory_id"] == subcategory_id
    assert data["subcategory_name"] == "Sub"
    assert data["hangout_id"] is None
    assert data["hangout_name"] is None

    r = client.get("/transactions/", headers=headers)
    assert r.status_code == 200
    list_after_create = r.json()
    assert any(t["id"] == tx_id for t in list_after_create)

    r = client.get(f"/transactions/{tx_id}", headers=headers)
    assert r.status_code == 200
    get_data = r.json()
    assert get_data["value"] == -1000
    assert get_data["subcategory_id"] == subcategory_id
    assert get_data["subcategory_name"] == "Sub"
    assert get_data["hangout_id"] is None
    assert get_data["hangout_name"] is None

    r = client.patch(
        f"/transactions/{tx_id}",
        headers=headers,
        json={"value": -1200, "description": "Coffee & cake"},
    )
    assert r.status_code == 200
    assert r.json()["value"] == -1200

    r = client.delete(f"/transactions/{tx_id}", headers=headers)
    assert r.status_code == 204

    r = client.get(f"/transactions/{tx_id}", headers=headers)
    assert r.status_code == 404


def test_transactions_get_404_when_not_owned(
    client: TestClient, clean_db: None, subcategory_id: str
) -> None:
    """GET /transactions/{id} returns 404 when transaction belongs to another user."""
    r = client.post(
        "/transactions/",
        headers={"X-Test-User-Id": "user-a"},
        json={
            "subcategory_id": subcategory_id,
            "value": 1,
            "description": "x",
            "date": "2025-01-01",
            "hangout_id": None,
        },
    )
    # subcategory was created by test-user-tx, so user-a doesn't own it → 404 on create
    # Create own chain for user-a
    r = client.post(
        "/categories/",
        headers={"X-Test-User-Id": "user-a"},
        json={"name": "C", "description": None, "is_income": False},
    )
    assert r.status_code == 201
    cat_id = r.json()["id"]
    r = client.post(
        "/subcategories/",
        headers={"X-Test-User-Id": "user-a"},
        json={"category_id": cat_id, "name": "S", "description": None, "belongs_to_income": False},
    )
    assert r.status_code == 201
    sub_a_id = r.json()["id"]
    r = client.post(
        "/transactions/",
        headers={"X-Test-User-Id": "user-a"},
        json={
            "subcategory_id": sub_a_id,
            "value": 1,
            "description": "x",
            "date": "2025-01-01",
            "hangout_id": None,
        },
    )
    assert r.status_code == 201
    tx_id = r.json()["id"]

    r = client.get(f"/transactions/{tx_id}", headers={"X-Test-User-Id": "user-b"})
    assert r.status_code == 404


def test_bulk_create_transactions_201_and_returns_list(
    client: TestClient, clean_db: None, subcategory_id: str
) -> None:
    """POST /transactions/bulk returns 201 and list of TransactionRead in order."""
    headers = {"X-Test-User-Id": "test-user-tx"}
    body = {
        "transactions": [
            {
                "subcategory_id": subcategory_id,
                "value": -100,
                "description": "Bulk A",
                "date": "2025-04-01",
                "hangout_id": None,
            },
            {
                "subcategory_id": subcategory_id,
                "value": -200,
                "description": "Bulk B",
                "date": "2025-04-02",
                "hangout_id": None,
            },
        ]
    }
    r = client.post("/transactions/bulk", headers=headers, json=body)
    assert r.status_code == 201
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["value"] == -100 and data[0]["description"] == "Bulk A"
    assert data[1]["value"] == -200 and data[1]["description"] == "Bulk B"
    assert data[0]["subcategory_id"] == subcategory_id
    created_ids = {data[0]["id"], data[1]["id"]}
    r = client.get("/transactions/", headers=headers)
    assert r.status_code == 200
    list_data = r.json()
    assert created_ids <= {t["id"] for t in list_data}


def test_bulk_create_transactions_without_auth_returns_401(
    client: TestClient, clean_db: None, subcategory_id: str
) -> None:
    """POST /transactions/bulk returns 401 without X-Test-User-Id."""
    body = {
        "transactions": [
            {
                "subcategory_id": subcategory_id,
                "value": 1,
                "description": "x",
                "date": "2025-01-01",
                "hangout_id": None,
            },
        ]
    }
    r = client.post("/transactions/bulk", json=body)
    assert r.status_code == 401


def test_bulk_create_transactions_404_when_subcategory_not_owned(
    client: TestClient, clean_db: None
) -> None:
    """POST /transactions/bulk returns 404 when body references subcategory not owned."""
    # Create category + subcategory as user-a
    r = client.post(
        "/categories/",
        headers={"X-Test-User-Id": "user-a"},
        json={"name": "C", "description": None, "is_income": False},
    )
    assert r.status_code == 201
    cat_id = r.json()["id"]
    r = client.post(
        "/subcategories/",
        headers={"X-Test-User-Id": "user-a"},
        json={
            "category_id": cat_id,
            "name": "S",
            "description": None,
            "belongs_to_income": False,
        },
    )
    assert r.status_code == 201
    sub_a_id = r.json()["id"]
    # user-b tries to create transactions with user-a's subcategory
    body = {
        "transactions": [
            {
                "subcategory_id": sub_a_id,
                "value": 1,
                "description": "x",
                "date": "2025-01-01",
                "hangout_id": None,
            },
        ]
    }
    r = client.post(
        "/transactions/bulk",
        headers={"X-Test-User-Id": "user-b"},
        json=body,
    )
    assert r.status_code == 404


def test_bulk_create_transactions_invalid_body_422(client: TestClient, clean_db: None) -> None:
    """POST /transactions/bulk returns 422 when body is invalid (e.g. missing required field)."""
    r = client.post(
        "/transactions/bulk",
        headers={"X-Test-User-Id": "test-user"},
        json={
            "transactions": [
                {
                    "subcategory_id": "not-a-uuid",
                    "value": 1,
                    "description": "x",
                    "date": "2025-01-01",
                },
            ]
        },
    )
    assert r.status_code == 422
