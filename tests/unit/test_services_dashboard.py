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


# --- Balance (§1.3 Dashboard) ---


def test_get_cumulative_balance_empty(db_session: Session) -> None:
    """No transactions → balance 0."""
    result = dashboard_service.get_cumulative_balance(db_session, "user-1")
    assert result.balance == 0


def test_get_cumulative_balance_income_minus_expense(db_session: Session) -> None:
    """Income subcategory adds value, expense subcategory subtracts value."""
    cat_inc = category_service.create_category(
        db_session, "user-1", CategoryCreate(name="Salary", description=None, is_income=True)
    )
    cat_exp = category_service.create_category(
        db_session, "user-1", CategoryCreate(name="Bills", description=None, is_income=False)
    )
    sub_inc = subcategory_service.create_subcategory(
        db_session,
        "user-1",
        SubcategoryCreate(
            category_id=cat_inc.id,
            name="Pay",
            description=None,
            belongs_to_income=True,
            is_periodic=False,
            due_day=None,
        ),
    )
    sub_exp = subcategory_service.create_subcategory(
        db_session,
        "user-1",
        SubcategoryCreate(
            category_id=cat_exp.id,
            name="Rent",
            description=None,
            belongs_to_income=False,
            is_periodic=False,
            due_day=None,
        ),
    )
    transaction_service.create_transaction(
        db_session,
        "user-1",
        TransactionCreate(
            subcategory_id=sub_inc.id,
            value=5000,
            description="Salary",
            date=date(2025, 6, 1),
        ),
    )
    transaction_service.create_transaction(
        db_session,
        "user-1",
        TransactionCreate(
            subcategory_id=sub_exp.id,
            value=1200,
            description="Rent",
            date=date(2025, 6, 5),
        ),
    )
    result = dashboard_service.get_cumulative_balance(db_session, "user-1")
    assert result.balance == 5000 - 1200


def test_get_month_balance_empty_month(db_session: Session) -> None:
    """No transactions in month → month balance 0."""
    result = dashboard_service.get_month_balance(db_session, "user-1", 2025, 6)
    assert result.balance == 0
    assert result.year == 2025
    assert result.month == 6


def test_get_month_balance_only_in_month(db_session: Session) -> None:
    """Month balance includes only transactions in that month."""
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
            is_periodic=False,
            due_day=None,
        ),
    )
    transaction_service.create_transaction(
        db_session,
        "user-1",
        TransactionCreate(
            subcategory_id=sub.id,
            value=100,
            description="June",
            date=date(2025, 6, 15),
        ),
    )
    transaction_service.create_transaction(
        db_session,
        "user-1",
        TransactionCreate(
            subcategory_id=sub.id,
            value=50,
            description="May",
            date=date(2025, 5, 15),
        ),
    )
    result_june = dashboard_service.get_month_balance(db_session, "user-1", 2025, 6)
    assert result_june.balance == -100
    result_may = dashboard_service.get_month_balance(db_session, "user-1", 2025, 5)
    assert result_may.balance == -50
