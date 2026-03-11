"""Dashboard service: balance and due-periodic-expenses. TECHSPEC §3.3, §4.3."""

from __future__ import annotations

from datetime import date

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session, joinedload

from app.models.subcategory import Subcategory
from app.models.transaction import Transaction
from app.schemas.dashboard import (
    DashboardBalanceRead,
    DashboardDuePeriodicExpenseRead,
    DashboardMonthBalanceRead,
)


def get_cumulative_balance(db: Session, user_id: str) -> DashboardBalanceRead:
    """
    Return cumulative net balance: sum of transaction values for income subcategories
    minus sum for expense subcategories. Same unit as Transaction.value.
    """
    stmt = (
        select(
            func.coalesce(
                func.sum(
                    case(
                        (Subcategory.belongs_to_income.is_(True), Transaction.value),
                        else_=-Transaction.value,
                    )
                ),
                0,
            )
        )
        .select_from(Transaction)
        .join(Subcategory, Transaction.subcategory_id == Subcategory.id)
        .where(Transaction.user_id == user_id)
    )
    total = db.execute(stmt).scalar()
    return DashboardBalanceRead(balance=int(total or 0))


def get_month_balance(
    db: Session, user_id: str, year: int, month: int
) -> DashboardMonthBalanceRead:
    """
    Return net balance for the given (year, month): same sign convention as
    get_cumulative_balance, restricted to transactions in that month.
    """
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    stmt = (
        select(
            func.coalesce(
                func.sum(
                    case(
                        (Subcategory.belongs_to_income.is_(True), Transaction.value),
                        else_=-Transaction.value,
                    )
                ),
                0,
            )
        )
        .select_from(Transaction)
        .join(Subcategory, Transaction.subcategory_id == Subcategory.id)
        .where(
            Transaction.user_id == user_id,
            Transaction.date >= start,
            Transaction.date < end,
        )
    )
    total = db.execute(stmt).scalar()
    return DashboardMonthBalanceRead(balance=int(total or 0), year=year, month=month)


def get_due_periodic_expenses(
    db: Session,
    user_id: str,
    year: int,
    month: int,
) -> list[DashboardDuePeriodicExpenseRead]:
    """
    Return all periodic subcategories for the user with a paid flag for the given month.
    Paid = at least one transaction for that subcategory in that (year, month). §3.3.
    """
    # First day and first day of next month for range
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)

    stmt = (
        select(Subcategory)
        .where(Subcategory.user_id == user_id, Subcategory.is_periodic.is_(True))
        .options(joinedload(Subcategory.category))
        .order_by(Subcategory.name)
    )
    rows = db.execute(stmt).unique().scalars().all()

    if not rows:
        return []

    subcategory_ids = [r.id for r in rows]
    # Subcategory IDs that have at least one transaction in [start, end)
    paid_stmt = (
        select(Transaction.subcategory_id)
        .where(
            Transaction.user_id == user_id,
            Transaction.subcategory_id.in_(subcategory_ids),
            Transaction.date >= start,
            Transaction.date < end,
        )
        .distinct()
    )
    paid_ids = set(db.execute(paid_stmt).scalars().all())

    return [
        DashboardDuePeriodicExpenseRead(
            subcategory_id=r.id,
            subcategory_name=r.name,
            category_id=r.category_id,
            category_name=r.category.name if r.category else "",
            due_day=r.due_day,
            paid=r.id in paid_ids,
        )
        for r in rows
    ]
