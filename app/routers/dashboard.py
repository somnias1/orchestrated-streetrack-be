"""Dashboard router: balance and due periodic expenses. TECHSPEC §3.6, §4.3."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import CurrentUserId
from app.db.session import get_db
from app.schemas.dashboard import (
    DashboardBalanceRead,
    DashboardDuePeriodicExpenseRead,
    DashboardMonthBalanceRead,
)
from app.services import dashboard as dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/balance", response_model=DashboardBalanceRead)
def get_balance(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
) -> DashboardBalanceRead:
    """Cumulative net balance (income − expense) for the authenticated user."""
    return dashboard_service.get_cumulative_balance(db, user_id)


@router.get("/month-balance", response_model=DashboardMonthBalanceRead)
def get_month_balance(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    year: Annotated[int, Query(ge=1, le=9999)],
    month: Annotated[int, Query(ge=1, le=12)],
) -> DashboardMonthBalanceRead:
    """Net balance for the given year and month."""
    return dashboard_service.get_month_balance(db, user_id, year, month)


@router.get("/due-periodic-expenses", response_model=list[DashboardDuePeriodicExpenseRead])
def get_due_periodic_expenses(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    year: Annotated[int, Query(ge=1, le=9999)],
    month: Annotated[int, Query(ge=1, le=12)],
) -> list[DashboardDuePeriodicExpenseRead]:
    """Periodic subcategories with paid flag for the given month."""
    return dashboard_service.get_due_periodic_expenses(db, user_id, year, month)
