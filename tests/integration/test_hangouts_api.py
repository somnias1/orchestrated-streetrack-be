"""
Integration: Hangouts API — one full flow. §1.3 CRUD scoped; 404 when not owned.
"""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_hangouts_flow(client: TestClient, clean_db: None) -> None:
    """List (empty) → create → list → get → update → delete → get 404."""
    headers = {"X-Test-User-Id": "test-user-hangouts"}

    r = client.get("/hangouts/", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["items"] == []
    assert body["total"] == 0
    assert body["has_more"] is False
    assert body["next_skip"] is None

    r = client.post(
        "/hangouts/",
        headers=headers,
        json={"name": "Beach day", "date": "2025-06-15", "description": "Fun"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Beach day"
    hang_id = data["id"]

    r = client.get("/hangouts/", headers=headers)
    assert r.status_code == 200
    listed = r.json()
    assert len(listed["items"]) == 1
    assert listed["total"] == 1
    assert listed["has_more"] is False
    assert listed["next_skip"] is None

    r = client.get(f"/hangouts/{hang_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Beach day"

    r = client.patch(
        f"/hangouts/{hang_id}",
        headers=headers,
        json={"name": "Beach & BBQ", "description": "Updated"},
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Beach & BBQ"

    r = client.delete(f"/hangouts/{hang_id}", headers=headers)
    assert r.status_code == 204

    r = client.get(f"/hangouts/{hang_id}", headers=headers)
    assert r.status_code == 404


def test_hangouts_get_404_when_not_owned(client: TestClient, clean_db: None) -> None:
    """GET /hangouts/{id} returns 404 when hangout belongs to another user."""
    r = client.post(
        "/hangouts/",
        headers={"X-Test-User-Id": "user-a"},
        json={"name": "Mine", "date": "2025-01-01", "description": None},
    )
    assert r.status_code == 201
    hang_id = r.json()["id"]

    r = client.get(f"/hangouts/{hang_id}", headers={"X-Test-User-Id": "user-b"})
    assert r.status_code == 404
