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
from app.schemas.transaction import (
    TransactionBulkCreate,
    TransactionCreate,
    TransactionUpdate,
)
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
    """List returns empty page when user has no transactions."""
    result = transaction_service.list_transactions(db_session, "user-1")
    assert result.items == []
    assert result.total == 0
    assert result.has_more is False
    assert result.next_skip is None


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
    assert len(list_a.items) == 1 and list_a.items[0].value == 100 and list_a.total == 1
    assert list_a.items[0].subcategory_name == "Sub"
    assert len(list_b.items) == 1 and list_b.items[0].value == 200 and list_b.total == 1
    assert list_b.items[0].subcategory_name == "Sub"


def test_list_transactions_newest_first(db_session: Session) -> None:
    """§1.3: List returns transactions ordered by date descending (newest first)."""
    cat = _make_category(db_session, "user-1")
    sub = _make_subcategory(db_session, "user-1", cat.id)
    transaction_service.create_transaction(
        db_session,
        "user-1",
        TransactionCreate(
            subcategory_id=sub.id,
            value=1,
            description="Old",
            date=date(2024, 6, 1),
            hangout_id=None,
        ),
    )
    transaction_service.create_transaction(
        db_session,
        "user-1",
        TransactionCreate(
            subcategory_id=sub.id,
            value=2,
            description="New",
            date=date(2025, 6, 1),
            hangout_id=None,
        ),
    )
    result = transaction_service.list_transactions(db_session, "user-1")
    assert len(result.items) == 2 and result.total == 2
    assert result.items[0].date == date(2025, 6, 1) and result.items[0].description == "New"
    assert result.items[1].date == date(2024, 6, 1) and result.items[1].description == "Old"


def test_list_transactions_filter_by_date_tree(db_session: Session) -> None:
    """§1.3: List with year/month/day filters returns only matching transactions."""
    cat = _make_category(db_session, "user-1")
    sub = _make_subcategory(db_session, "user-1", cat.id)
    transaction_service.create_transaction(
        db_session,
        "user-1",
        TransactionCreate(
            subcategory_id=sub.id,
            value=1,
            description="2024",
            date=date(2024, 3, 15),
            hangout_id=None,
        ),
    )
    transaction_service.create_transaction(
        db_session,
        "user-1",
        TransactionCreate(
            subcategory_id=sub.id,
            value=2,
            description="2025",
            date=date(2025, 3, 15),
            hangout_id=None,
        ),
    )
    by_year = transaction_service.list_transactions(db_session, "user-1", year=2025)
    assert len(by_year.items) == 1 and by_year.total == 1 and by_year.items[0].description == "2025"
    by_month = transaction_service.list_transactions(db_session, "user-1", month=3)
    assert len(by_month.items) == 2 and by_month.total == 2
    by_year_month = transaction_service.list_transactions(db_session, "user-1", year=2025, month=3)
    assert len(by_year_month.items) == 1 and by_year_month.items[0].description == "2025"
    by_day = transaction_service.list_transactions(db_session, "user-1", year=2025, month=3, day=15)
    assert len(by_day.items) == 1 and by_day.items[0].date == date(2025, 3, 15)


def test_list_transactions_filter_by_subcategory_id(db_session: Session) -> None:
    """§1.3: List with subcategory_id returns only transactions for that subcategory."""
    cat = _make_category(db_session, "user-1")
    sub1 = _make_subcategory(db_session, "user-1", cat.id)
    sub2 = subcategory_service.create_subcategory(
        db_session,
        "user-1",
        SubcategoryCreate(
            category_id=cat.id, name="Sub2", description=None, belongs_to_income=False
        ),
    )
    transaction_service.create_transaction(
        db_session,
        "user-1",
        TransactionCreate(
            subcategory_id=sub1.id,
            value=10,
            description="S1",
            date=date(2025, 1, 1),
            hangout_id=None,
        ),
    )
    transaction_service.create_transaction(
        db_session,
        "user-1",
        TransactionCreate(
            subcategory_id=sub2.id,
            value=20,
            description="S2",
            date=date(2025, 1, 2),
            hangout_id=None,
        ),
    )
    by_sub1 = transaction_service.list_transactions(db_session, "user-1", subcategory_id=sub1.id)
    assert len(by_sub1.items) == 1 and by_sub1.total == 1
    assert by_sub1.items[0].subcategory_id == sub1.id and by_sub1.items[0].value == 10


def test_list_transactions_filter_by_hangout_id(db_session: Session) -> None:
    """§1.3: List with hangout_id returns only transactions linked to that hangout."""
    cat = _make_category(db_session, "user-1")
    sub = _make_subcategory(db_session, "user-1", cat.id)
    hang1 = _make_hangout(db_session, "user-1")
    hang2 = hangout_service.create_hangout(
        db_session, "user-1", HangoutCreate(name="H2", date=date(2025, 2, 1), description=None)
    )
    transaction_service.create_transaction(
        db_session,
        "user-1",
        TransactionCreate(
            subcategory_id=sub.id,
            value=1,
            description="H1",
            date=date(2025, 1, 1),
            hangout_id=hang1.id,
        ),
    )
    transaction_service.create_transaction(
        db_session,
        "user-1",
        TransactionCreate(
            subcategory_id=sub.id,
            value=2,
            description="H2",
            date=date(2025, 1, 2),
            hangout_id=hang2.id,
        ),
    )
    transaction_service.create_transaction(
        db_session,
        "user-1",
        TransactionCreate(
            subcategory_id=sub.id,
            value=3,
            description="NoHang",
            date=date(2025, 1, 3),
            hangout_id=None,
        ),
    )
    by_hang1 = transaction_service.list_transactions(db_session, "user-1", hangout_id=hang1.id)
    assert len(by_hang1.items) == 1 and by_hang1.total == 1
    assert by_hang1.items[0].hangout_id == hang1.id and by_hang1.items[0].value == 1


def test_list_transactions_pagination_total_skip_and_has_more(db_session: Session) -> None:
    """total counts filtered rows; skip/limit slice; has_more and next_skip set."""
    cat = _make_category(db_session, "user-1")
    sub = _make_subcategory(db_session, "user-1", cat.id)
    for d, desc in (
        (date(2025, 1, 1), "A"),
        (date(2025, 1, 2), "B"),
        (date(2025, 1, 3), "C"),
    ):
        transaction_service.create_transaction(
            db_session,
            "user-1",
            TransactionCreate(
                subcategory_id=sub.id,
                value=1,
                description=desc,
                date=d,
                hangout_id=None,
            ),
        )
    p1 = transaction_service.list_transactions(db_session, "user-1", skip=0, limit=2)
    assert len(p1.items) == 2 and p1.total == 3
    assert p1.has_more is True and p1.next_skip == 2
    p2 = transaction_service.list_transactions(db_session, "user-1", skip=2, limit=2)
    assert len(p2.items) == 1 and p2.total == 3
    assert p2.has_more is False and p2.next_skip is None


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
    assert result.subcategory_id == sub.id
    assert result.subcategory_name == "Sub"
    assert result.hangout_id is None
    assert result.hangout_name is None


def test_create_transaction_with_hangout_returns_hangout_name(db_session: Session) -> None:
    """Read response includes hangout_id and hangout_name when linked to a hangout."""
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
    assert result.subcategory_id == sub.id
    assert result.subcategory_name == "Sub"
    assert result.hangout_id == hang.id
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


def test_bulk_create_transactions_success(db_session: Session) -> None:
    """Bulk create persists all items when all subcategories/hangouts are owned."""
    cat = _make_category(db_session, "user-1")
    sub = _make_subcategory(db_session, "user-1", cat.id)
    body = TransactionBulkCreate(
        transactions=[
            TransactionCreate(
                subcategory_id=sub.id,
                value=10,
                description="A",
                date=date(2025, 1, 1),
                hangout_id=None,
            ),
            TransactionCreate(
                subcategory_id=sub.id,
                value=20,
                description="B",
                date=date(2025, 1, 2),
                hangout_id=None,
            ),
        ]
    )
    result = transaction_service.bulk_create_transactions(db_session, "user-1", body)
    assert len(result) == 2
    assert result[0].value == 10 and result[0].description == "A"
    assert result[1].value == 20 and result[1].description == "B"
    assert result[0].subcategory_id == sub.id and result[1].subcategory_id == sub.id
    list_all = transaction_service.list_transactions(db_session, "user-1")
    assert len(list_all.items) == 2 and list_all.total == 2


def test_bulk_create_transactions_404_when_subcategory_not_owned(
    db_session: Session,
) -> None:
    """Bulk create returns 404 when an item references a subcategory not owned by user."""
    cat_other = _make_category(db_session, "user-other")
    sub_other = _make_subcategory(db_session, "user-other", cat_other.id)
    body = TransactionBulkCreate(
        transactions=[
            TransactionCreate(
                subcategory_id=sub_other.id,
                value=1,
                description="x",
                date=date(2025, 1, 1),
                hangout_id=None,
            ),
        ]
    )
    with pytest.raises(HTTPException) as exc_info:
        transaction_service.bulk_create_transactions(db_session, "user-1", body)
    assert exc_info.value.status_code == 404
    assert transaction_service.list_transactions(db_session, "user-1").total == 0


def test_bulk_create_transactions_404_when_hangout_not_owned(db_session: Session) -> None:
    """Bulk create returns 404 when an item references a hangout not owned by user."""
    cat = _make_category(db_session, "user-1")
    sub = _make_subcategory(db_session, "user-1", cat.id)
    hang_other = _make_hangout(db_session, "user-other")
    body = TransactionBulkCreate(
        transactions=[
            TransactionCreate(
                subcategory_id=sub.id,
                value=1,
                description="x",
                date=date(2025, 1, 1),
                hangout_id=hang_other.id,
            ),
        ]
    )
    with pytest.raises(HTTPException) as exc_info:
        transaction_service.bulk_create_transactions(db_session, "user-1", body)
    assert exc_info.value.status_code == 404
    assert transaction_service.list_transactions(db_session, "user-1").total == 0


def test_bulk_create_transactions_all_or_nothing(db_session: Session) -> None:
    """Bulk create creates no rows when a later item fails ownership (404 before any insert)."""
    cat = _make_category(db_session, "user-1")
    sub = _make_subcategory(db_session, "user-1", cat.id)
    cat_other = _make_category(db_session, "user-other")
    sub_other = _make_subcategory(db_session, "user-other", cat_other.id)
    body = TransactionBulkCreate(
        transactions=[
            TransactionCreate(
                subcategory_id=sub.id,
                value=10,
                description="OK",
                date=date(2025, 1, 1),
                hangout_id=None,
            ),
            TransactionCreate(
                subcategory_id=sub_other.id,
                value=20,
                description="Bad",
                date=date(2025, 1, 2),
                hangout_id=None,
            ),
        ]
    )
    with pytest.raises(HTTPException) as exc_info:
        transaction_service.bulk_create_transactions(db_session, "user-1", body)
    assert exc_info.value.status_code == 404
    list_user1 = transaction_service.list_transactions(db_session, "user-1")
    assert list_user1.total == 0 and list_user1.items == []
