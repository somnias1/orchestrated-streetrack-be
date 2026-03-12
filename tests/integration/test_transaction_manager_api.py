"""
Integration: Transaction manager API — import preview and CSV export. §1.3.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def category_subcategory_ids(client: TestClient, clean_db: None) -> tuple[str, str]:
    """Create category + subcategory for test-user-tm; return (category_name, subcategory_id)."""
    r = client.post(
        "/categories/",
        headers={"X-Test-User-Id": "test-user-tm"},
        json={"name": "Food", "description": None, "is_income": False},
    )
    assert r.status_code == 201
    cat_id = r.json()["id"]
    r = client.post(
        "/subcategories/",
        headers={"X-Test-User-Id": "test-user-tm"},
        json={
            "category_id": cat_id,
            "name": "Groceries",
            "description": None,
            "belongs_to_income": False,
        },
    )
    assert r.status_code == 201
    sub_id = r.json()["id"]
    return "Food", sub_id


def test_import_preview_200_returns_payload(
    client: TestClient, clean_db: None, category_subcategory_ids: tuple[str, str]
) -> None:
    """POST /transaction-manager/import returns 200 with transactions and invalid_rows."""
    cat_name, sub_id = category_subcategory_ids
    headers = {"X-Test-User-Id": "test-user-tm"}
    body = {
        "rows": [
            {
                "category_name": cat_name,
                "subcategory_name": "Groceries",
                "value": -100,
                "description": "Import row",
                "date": "2025-03-10",
                "hangout_id": None,
            },
        ]
    }
    r = client.post("/transaction-manager/import", headers=headers, json=body)
    assert r.status_code == 200
    data = r.json()
    assert "transactions" in data
    assert "invalid_rows" in data
    assert len(data["transactions"]) == 1
    # subcategory_id may differ when multiple (category, subcategory) pairs exist in shared test DB
    assert data["transactions"][0]["subcategory_id"] is not None
    assert data["transactions"][0]["value"] == -100
    assert data["invalid_rows"] == []


def test_import_preview_invalid_pair_invalid_rows(
    client: TestClient, clean_db: None
) -> None:
    """POST /transaction-manager/import returns invalid_rows for unknown category/subcategory."""
    headers = {"X-Test-User-Id": "test-user-tm"}
    body = {
        "rows": [
            {
                "category_name": "NoSuch",
                "subcategory_name": "Sub",
                "value": -1,
                "description": "x",
                "date": "2025-01-01",
                "hangout_id": None,
            },
        ]
    }
    r = client.post("/transaction-manager/import", headers=headers, json=body)
    assert r.status_code == 200
    data = r.json()
    assert data["transactions"] == []
    assert len(data["invalid_rows"]) == 1
    assert data["invalid_rows"][0]["row_index"] == 0


def test_import_preview_without_auth_returns_401(
    client: TestClient, clean_db: None, category_subcategory_ids: tuple[str, str]
) -> None:
    """POST /transaction-manager/import returns 401 without auth."""
    cat_name, _ = category_subcategory_ids
    body = {
        "rows": [
            {
                "category_name": cat_name,
                "subcategory_name": "Groceries",
                "value": -1,
                "description": "x",
                "date": "2025-01-01",
                "hangout_id": None,
            },
        ]
    }
    r = client.post("/transaction-manager/import", json=body)
    assert r.status_code == 401


def test_export_returns_csv_200(
    client: TestClient, clean_db: None, category_subcategory_ids: tuple[str, str]
) -> None:
    """GET /transaction-manager/export returns 200 and text/csv with header."""
    _, sub_id = category_subcategory_ids
    headers = {"X-Test-User-Id": "test-user-tm"}
    # Create one transaction
    r = client.post(
        "/transactions/",
        headers=headers,
        json={
            "subcategory_id": sub_id,
            "value": -50,
            "description": "Export test",
            "date": "2025-03-01",
            "hangout_id": None,
        },
    )
    assert r.status_code == 201

    r = client.get("/transaction-manager/export", headers=headers)
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("content-type", "")
    lines = r.text.strip().split("\n")
    assert len(lines) >= 1
    assert "date" in lines[0]
    assert "subcategory_id" in lines[0]
    if len(lines) > 1:
        assert "2025-03-01" in lines[1] or "Export test" in lines[1]


def test_export_without_auth_returns_401(client: TestClient, clean_db: None) -> None:
    """GET /transaction-manager/export returns 401 without auth."""
    r = client.get("/transaction-manager/export")
    assert r.status_code == 401
