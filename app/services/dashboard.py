"""Dashboard service: due-periodic-expenses business logic. TECHSPEC §3.3, §4.3."""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.subcategory import Subcategory
from app.models.transaction import Transaction
from app.schemas.dashboard import DashboardDuePeriodicExpenseRead


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
