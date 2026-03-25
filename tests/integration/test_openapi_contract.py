"""
Integration: OpenAPI contract — finance expansion endpoints and schemas exposed for FE. §1.3, §4.3.
"""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_openapi_exposes_finance_endpoints(client: TestClient) -> None:
    """GET /openapi.json exposes dashboard and transaction-manager paths for FE contract."""
    r = client.get("/openapi.json")
    assert r.status_code == 200
    openapi = r.json()
    paths = openapi.get("paths", {})
    # Dashboard (§4.3)
    assert "/dashboard/balance" in paths
    assert "/dashboard/month-balance" in paths
    assert "/dashboard/due-periodic-expenses" in paths
    # Transaction manager
    assert "/transaction-manager/import" in paths
    assert "/transaction-manager/export" in paths
    # Transactions list (paginated) + bulk
    assert "get" in paths["/transactions/"]
    assert "/transactions/bulk" in paths
    # Paths have get/post and expected response schemas
    assert "get" in paths["/dashboard/balance"]
    assert "get" in paths["/dashboard/month-balance"]
    assert "get" in paths["/dashboard/due-periodic-expenses"]
    assert "post" in paths["/transaction-manager/import"]
    assert "get" in paths["/transaction-manager/export"]
    assert "post" in paths["/transactions/bulk"]
