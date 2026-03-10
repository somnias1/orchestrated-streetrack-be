"""
Unit tests for Dashboard service. §1.3: due-periodic-expenses paid-for-month rule.
"""

from __future__ import annotations

from datetime import date

from app.schemas.category import CategoryCreate
from app.schemas.subcategory import SubcategoryCreate
from app.schemas.transaction import TransactionCreate
from app.services import category as category_service
from app.services import dashboard as dashboard_service
from app.services import subcategory as subcategory_service
from app.services import transaction as transaction_service
from sqlalchemy.orm import Session


def test_get_due_periodic_expenses_empty_when_no_periodic(db_session: Session) -> None:
    """When user has no periodic subcategories, returns empty list."""
    result = dashboard_service.get_due_periodic_expenses(
        db_session, "user-1", year=2025, month=6
    )
    assert result == []


def test_get_due_periodic_expenses_unpaid_when_no_transaction_in_month(
    db_session: Session,
) -> None:
    """§1.3 due-status: one periodic subcategory, no transaction in month M → paid=false."""
    cat = category_service.create_category(
        db_session, "user-1", CategoryCreate(name="Bills", description=None, is_income=False)
    )
    sub = subcategory_service.create_subcategory(
        db_session,
        "user-1",
        SubcategoryCreate(
            category_id=cat.id,
            name="Rent",
            description=None,
            belongs_to_income=False,
            is_periodic=True,
            due_day=5,
        ),
    )
    result = dashboard_service.get_due_periodic_expenses(
        db_session, "user-1", year=2025, month=6
    )
    assert len(result) == 1
    assert result[0].subcategory_id == sub.id
    assert result[0].subcategory_name == "Rent"
    assert result[0].due_day == 5
    assert result[0].paid is False


def test_get_due_periodic_expenses_paid_when_transaction_in_month(
    db_session: Session,
) -> None:
    """§1.3 due-status: one periodic subcategory, one transaction in month M → paid=true."""
    cat = category_service.create_category(
        db_session, "user-1", CategoryCreate(name="Bills", description=None, is_income=False)
    )
    sub = subcategory_service.create_subcategory(
        db_session,
        "user-1",
        SubcategoryCreate(
            category_id=cat.id,
            name="Rent",
            description=None,
            belongs_to_income=False,
            is_periodic=True,
            due_day=5,
        ),
    )
    transaction_service.create_transaction(
        db_session,
        "user-1",
        TransactionCreate(
            subcategory_id=sub.id,
            value=-1000,
            description="June rent",
            date=date(2025, 6, 10),
        ),
    )
    result = dashboard_service.get_due_periodic_expenses(
        db_session, "user-1", year=2025, month=6
    )
    assert len(result) == 1
    assert result[0].paid is True


def test_get_due_periodic_expenses_ignores_other_months(db_session: Session) -> None:
    """Transaction in another month does not set paid for the selected month."""
    cat = category_service.create_category(
        db_session, "user-1", CategoryCreate(name="Bills", description=None, is_income=False)
    )
    sub = subcategory_service.create_subcategory(
        db_session,
        "user-1",
        SubcategoryCreate(
            category_id=cat.id,
            name="Rent",
            description=None,
            belongs_to_income=False,
            is_periodic=True,
            due_day=5,
        ),
    )
    transaction_service.create_transaction(
        db_session,
        "user-1",
        TransactionCreate(
            subcategory_id=sub.id,
            value=-1000,
            description="May rent",
            date=date(2025, 5, 10),
        ),
    )
    result = dashboard_service.get_due_periodic_expenses(
        db_session, "user-1", year=2025, month=6
    )
    assert len(result) == 1
    assert result[0].paid is False
