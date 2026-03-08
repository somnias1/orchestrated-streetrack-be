"""
Unit tests for Transaction service. §1.3: CRUD + subcategory/hangout ownership; 404 when not owned.
"""

from __future__ import annotations

import uuid
from datetime import date

import pytest
from app.schemas.category import CategoryCreate
from app.schemas.hangout import HangoutCreate
from app.schemas.subcategory import SubcategoryCreate
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.services import category as category_service
from app.services import hangout as hangout_service
from app.services import subcategory as subcategory_service
from app.services import transaction as transaction_service
from fastapi import HTTPException
from sqlalchemy.orm import Session


def _make_category(db: Session, user_id: str):
    return category_service.create_category(
        db, user_id, CategoryCreate(name="Cat", description=None, is_income=False)
    )


def _make_subcategory(db: Session, user_id: str, category_id: uuid.UUID):
    return subcategory_service.create_subcategory(
        db,
        user_id,
        SubcategoryCreate(
            category_id=category_id, name="Sub", description=None, belongs_to_income=False
        ),
    )


def _make_hangout(db: Session, user_id: str):
    return hangout_service.create_hangout(
        db, user_id, HangoutCreate(name="Hangout", date=date(2025, 1, 15), description=None)
    )


def test_list_transactions_empty(db_session: Session) -> None:
    """List returns empty when user has no transactions."""
    result = transaction_service.list_transactions(db_session, "user-1")
    assert result == []


def test_list_transactions_scoped(db_session: Session) -> None:
    """List returns only transactions for the given user_id."""
    cat_a = _make_category(db_session, "user-a")
    cat_b = _make_category(db_session, "user-b")
    sub_a = _make_subcategory(db_session, "user-a", cat_a.id)
    sub_b = _make_subcategory(db_session, "user-b", cat_b.id)
    transaction_service.create_transaction(
        db_session,
        "user-a",
        TransactionCreate(
            subcategory_id=sub_a.id,
            value=100,
            description="A",
            date=date(2025, 1, 1),
            hangout_id=None,
        ),
    )
    transaction_service.create_transaction(
        db_session,
        "user-b",
        TransactionCreate(
            subcategory_id=sub_b.id,
            value=200,
            description="B",
            date=date(2025, 1, 2),
            hangout_id=None,
        ),
    )
    list_a = transaction_service.list_transactions(db_session, "user-a")
    list_b = transaction_service.list_transactions(db_session, "user-b")
    assert len(list_a) == 1 and list_a[0].value == 100 and list_a[0].subcategory_name == "Sub"
    assert len(list_b) == 1 and list_b[0].value == 200 and list_b[0].subcategory_name == "Sub"


def test_get_transaction_404_when_not_owned(db_session: Session) -> None:
    """Get raises 404 when transaction exists but belongs to another user."""
    cat = _make_category(db_session, "user-owner")
    sub = _make_subcategory(db_session, "user-owner", cat.id)
    created = transaction_service.create_transaction(
        db_session,
        "user-owner",
        TransactionCreate(
            subcategory_id=sub.id,
            value=1,
            description="x",
            date=date(2025, 1, 1),
            hangout_id=None,
        ),
    )
    with pytest.raises(HTTPException) as exc_info:
        transaction_service.get_transaction(db_session, "user-other", created.id)
    assert exc_info.value.status_code == 404


def test_create_transaction_404_when_subcategory_not_owned(db_session: Session) -> None:
    """Create raises 404 when subcategory belongs to another user."""
    cat = _make_category(db_session, "user-owner")
    sub = _make_subcategory(db_session, "user-owner", cat.id)
    with pytest.raises(HTTPException) as exc_info:
        transaction_service.create_transaction(
            db_session,
            "user-other",
            TransactionCreate(
                subcategory_id=sub.id,
                value=1,
                description="x",
                date=date(2025, 1, 1),
                hangout_id=None,
            ),
        )
    assert exc_info.value.status_code == 404


def test_create_transaction_404_when_hangout_not_owned(db_session: Session) -> None:
    """Create raises 404 when hangout_id is set and hangout belongs to another user."""
    cat = _make_category(db_session, "user-1")
    sub = _make_subcategory(db_session, "user-1", cat.id)
    hang = _make_hangout(db_session, "user-other")
    with pytest.raises(HTTPException) as exc_info:
        transaction_service.create_transaction(
            db_session,
            "user-1",
            TransactionCreate(
                subcategory_id=sub.id,
                value=1,
                description="x",
                date=date(2025, 1, 1),
                hangout_id=hang.id,
            ),
        )
    assert exc_info.value.status_code == 404


def test_create_transaction_success(db_session: Session) -> None:
    """Create persists transaction when subcategory (and optional hangout) are owned."""
    cat = _make_category(db_session, "user-1")
    sub = _make_subcategory(db_session, "user-1", cat.id)
    result = transaction_service.create_transaction(
        db_session,
        "user-1",
        TransactionCreate(
            subcategory_id=sub.id,
            value=-50,
            description="Coffee",
            date=date(2025, 3, 1),
            hangout_id=None,
        ),
    )
    assert result.value == -50
    assert result.description == "Coffee"
    assert result.subcategory_name == "Sub"
    assert result.hangout_name is None


def test_create_transaction_with_hangout_returns_hangout_name(db_session: Session) -> None:
    """Read response includes hangout_name when transaction is linked to a hangout."""
    cat = _make_category(db_session, "user-1")
    sub = _make_subcategory(db_session, "user-1", cat.id)
    hang = _make_hangout(db_session, "user-1")
    result = transaction_service.create_transaction(
        db_session,
        "user-1",
        TransactionCreate(
            subcategory_id=sub.id,
            value=10,
            description="Outing",
            date=date(2025, 2, 1),
            hangout_id=hang.id,
        ),
    )
    assert result.subcategory_name == "Sub"
    assert result.hangout_name == "Hangout"


def test_update_transaction_404_when_not_owned(db_session: Session) -> None:
    """Update raises 404 when transaction belongs to another user."""
    cat = _make_category(db_session, "user-owner")
    sub = _make_subcategory(db_session, "user-owner", cat.id)
    created = transaction_service.create_transaction(
        db_session,
        "user-owner",
        TransactionCreate(
            subcategory_id=sub.id,
            value=1,
            description="x",
            date=date(2025, 1, 1),
            hangout_id=None,
        ),
    )
    with pytest.raises(HTTPException) as exc_info:
        transaction_service.update_transaction(
            db_session, "user-other", created.id, TransactionUpdate(value=999)
        )
    assert exc_info.value.status_code == 404


def test_delete_transaction_success(db_session: Session) -> None:
    """Delete removes transaction when owned."""
    cat = _make_category(db_session, "user-1")
    sub = _make_subcategory(db_session, "user-1", cat.id)
    created = transaction_service.create_transaction(
        db_session,
        "user-1",
        TransactionCreate(
            subcategory_id=sub.id,
            value=1,
            description="x",
            date=date(2025, 1, 1),
            hangout_id=None,
        ),
    )
    transaction_service.delete_transaction(db_session, "user-1", created.id)
    with pytest.raises(HTTPException) as exc_info:
        transaction_service.get_transaction(db_session, "user-1", created.id)
    assert exc_info.value.status_code == 404
