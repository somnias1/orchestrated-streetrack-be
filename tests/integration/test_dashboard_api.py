"""
Integration: Dashboard API — balance and due periodic expenses. §1.3 Dashboard.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-Test-User-Id": "test-user-dashboard"}


def test_dashboard_balance_without_auth_returns_401(client: TestClient) -> None:
    """GET /dashboard/balance without token returns 401."""
    r = client.get("/dashboard/balance")
    assert r.status_code == 401


def test_dashboard_balance_returns_shape(
    client: TestClient, clean_db: None, auth_headers: dict[str, str]
) -> None:
    """GET /dashboard/balance returns 200 and DashboardBalanceRead shape."""
    r = client.get("/dashboard/balance", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "balance" in data
    assert isinstance(data["balance"], int)


def test_dashboard_month_balance_without_auth_returns_401(client: TestClient) -> None:
    """GET /dashboard/month-balance without token returns 401."""
    r = client.get("/dashboard/month-balance", params={"year": 2025, "month": 6})
    assert r.status_code == 401


def test_dashboard_month_balance_returns_shape(
    client: TestClient, clean_db: None, auth_headers: dict[str, str]
) -> None:
    """GET /dashboard/month-balance returns 200 and DashboardMonthBalanceRead shape."""
    r = client.get(
        "/dashboard/month-balance",
        headers=auth_headers,
        params={"year": 2025, "month": 6},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["balance"] == 0
    assert data["year"] == 2025
    assert data["month"] == 6


def test_dashboard_month_balance_missing_year_422(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """GET /dashboard/month-balance without year returns 422."""
    r = client.get(
        "/dashboard/month-balance",
        headers=auth_headers,
        params={"month": 6},
    )
    assert r.status_code == 422


def test_dashboard_month_balance_missing_month_422(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """GET /dashboard/month-balance without month returns 422."""
    r = client.get(
        "/dashboard/month-balance",
        headers=auth_headers,
        params={"year": 2025},
    )
    assert r.status_code == 422


def test_dashboard_due_periodic_expenses_without_auth_returns_401(client: TestClient) -> None:
    """GET /dashboard/due-periodic-expenses without token returns 401."""
    r = client.get(
        "/dashboard/due-periodic-expenses",
        params={"year": 2025, "month": 6},
    )
    assert r.status_code == 401


def test_dashboard_due_periodic_expenses_returns_list(
    client: TestClient, clean_db: None, auth_headers: dict[str, str]
) -> None:
    """GET /dashboard/due-periodic-expenses returns 200 and list."""
    r = client.get(
        "/dashboard/due-periodic-expenses",
        headers=auth_headers,
        params={"year": 2025, "month": 6},
    )
    assert r.status_code == 200
    assert r.json() == []


def test_dashboard_due_periodic_expenses_missing_year_422(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """GET /dashboard/due-periodic-expenses without year returns 422."""
    r = client.get(
        "/dashboard/due-periodic-expenses",
        headers=auth_headers,
        params={"month": 6},
    )
    assert r.status_code == 422


def test_dashboard_due_periodic_expenses_missing_month_422(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """GET /dashboard/due-periodic-expenses without month returns 422."""
    r = client.get(
        "/dashboard/due-periodic-expenses",
        headers=auth_headers,
        params={"year": 2025},
    )
    assert r.status_code == 422
