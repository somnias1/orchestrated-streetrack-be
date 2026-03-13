"""
Unit tests for transaction_manager service. §1.3: import preview vs existing pairs; export CSV.
"""

from __future__ import annotations

import uuid
from datetime import date

from app.schemas.category import CategoryCreate
from app.schemas.hangout import HangoutCreate
from app.schemas.subcategory import SubcategoryCreate
from app.schemas.transaction import (
    TransactionCreate,
    TransactionImportRequest,
    TransactionImportRow,
)
from app.services import category as category_service
from app.services import hangout as hangout_service
from app.services import subcategory as subcategory_service
from app.services import transaction as transaction_service
from app.services import transaction_manager as tm_service
from sqlalchemy.orm import Session


def _make_category(db: Session, user_id: str, name: str = "Cat"):
    return category_service.create_category(
        db, user_id, CategoryCreate(name=name, description=None, is_income=False)
    )


def _make_subcategory(db: Session, user_id: str, category_id: uuid.UUID, name: str = "Sub"):
    return subcategory_service.create_subcategory(
        db,
        user_id,
        SubcategoryCreate(
            category_id=category_id, name=name, description=None, belongs_to_income=False
        ),
    )


def _make_hangout(db: Session, user_id: str):
    return hangout_service.create_hangout(
        db, user_id, HangoutCreate(name="H", date=date(2025, 1, 15), description=None)
    )


def test_preview_import_resolves_valid_row(db_session: Session) -> None:
    """Preview returns normalized TransactionCreate when category/subcategory pair exists."""
    cat = _make_category(db_session, "user-1", "Food")
    sub = _make_subcategory(db_session, "user-1", cat.id, "Groceries")
    req = TransactionImportRequest(
        rows=[
            TransactionImportRow(
                category_name="Food",
                subcategory_name="Groceries",
                value=-500,
                description="Milk",
                date=date(2025, 3, 10),
                hangout_id=None,
            ),
        ]
    )
    preview = tm_service.preview_import(db_session, "user-1", req)
    assert len(preview.transactions) == 1
    assert preview.transactions[0].subcategory_id == sub.id
    assert preview.transactions[0].value == -500
    assert preview.transactions[0].description == "Milk"
    assert preview.transactions[0].date == date(2025, 3, 10)
    assert preview.transactions[0].hangout_id is None
    assert preview.invalid_rows == []


def test_preview_import_invalid_pair_reported(db_session: Session) -> None:
    """Preview reports invalid_rows when category/subcategory pair not found."""
    req = TransactionImportRequest(
        rows=[
            TransactionImportRow(
                category_name="Unknown",
                subcategory_name="Sub",
                value=-1,
                description="x",
                date=date(2025, 1, 1),
                hangout_id=None,
            ),
        ]
    )
    preview = tm_service.preview_import(db_session, "user-1", req)
    assert preview.transactions == []
    assert len(preview.invalid_rows) == 1
    assert preview.invalid_rows[0].row_index == 0
    msg = preview.invalid_rows[0].message.lower()
    assert "not found" in msg or "not owned" in msg


def test_preview_import_mixed_valid_invalid(db_session: Session) -> None:
    """Preview returns valid transactions and invalid_rows for unresolved rows."""
    cat = _make_category(db_session, "user-1", "A")
    _make_subcategory(db_session, "user-1", cat.id, "B")
    req = TransactionImportRequest(
        rows=[
            TransactionImportRow(
                category_name="A",
                subcategory_name="B",
                value=1,
                description="ok",
                date=date(2025, 1, 1),
                hangout_id=None,
            ),
            TransactionImportRow(
                category_name="No",
                subcategory_name="Such",
                value=2,
                description="bad",
                date=date(2025, 1, 2),
                hangout_id=None,
            ),
        ]
    )
    preview = tm_service.preview_import(db_session, "user-1", req)
    assert len(preview.transactions) == 1
    assert preview.transactions[0].description == "ok"
    assert len(preview.invalid_rows) == 1
    assert preview.invalid_rows[0].row_index == 1


def test_preview_import_hangout_not_owned_reported(db_session: Session) -> None:
    """Preview reports invalid row when hangout_id is not owned by user."""
    cat = _make_category(db_session, "user-1", "C")
    _make_subcategory(db_session, "user-1", cat.id, "S")
    hang_other = _make_hangout(db_session, "user-other")
    req = TransactionImportRequest(
        rows=[
            TransactionImportRow(
                category_name="C",
                subcategory_name="S",
                value=-1,
                description="x",
                date=date(2025, 1, 1),
                hangout_id=hang_other.id,
            ),
        ]
    )
    preview = tm_service.preview_import(db_session, "user-1", req)
    assert preview.transactions == []
    assert len(preview.invalid_rows) == 1
    assert "hangout" in preview.invalid_rows[0].message.lower()


def test_preview_import_with_owned_hangout(db_session: Session) -> None:
    """Preview includes TransactionCreate with hangout_id when hangout is owned."""
    cat = _make_category(db_session, "user-1", "Cat")
    _make_subcategory(db_session, "user-1", cat.id, "Sub")
    hang = _make_hangout(db_session, "user-1")
    req = TransactionImportRequest(
        rows=[
            TransactionImportRow(
                category_name="Cat",
                subcategory_name="Sub",
                value=-10,
                description="With hangout",
                date=date(2025, 2, 1),
                hangout_id=hang.id,
            ),
        ]
    )
    preview = tm_service.preview_import(db_session, "user-1", req)
    assert len(preview.transactions) == 1
    assert preview.transactions[0].hangout_id == hang.id
    assert preview.invalid_rows == []


def test_export_transactions_csv_empty(db_session: Session) -> None:
    """Export returns header only when no transactions."""
    csv_str = tm_service.export_transactions_csv(db_session, "user-1")
    lines = csv_str.strip().split("\n")
    assert len(lines) >= 1
    assert "date" in lines[0] and "subcategory_id" in lines[0]


def test_export_transactions_csv_oldest_first(db_session: Session) -> None:
    """Export returns rows ordered oldest to newest."""
    cat = _make_category(db_session, "user-1", "C")
    sub = _make_subcategory(db_session, "user-1", cat.id, "S")
    dates_desc = [
        (date(2025, 3, 3), "Third"),
        (date(2025, 3, 1), "First"),
        (date(2025, 3, 2), "Second"),
    ]
    for d, desc in dates_desc:
        transaction_service.create_transaction(
            db_session,
            "user-1",
            TransactionCreate(
                subcategory_id=sub.id,
                value=-1,
                description=desc,
                date=d,
                hangout_id=None,
            ),
        )
    csv_str = tm_service.export_transactions_csv(db_session, "user-1")
    lines = csv_str.strip().split("\n")
    assert len(lines) == 4  # header + 3 rows
    # Order: First (3/1), Second (3/2), Third (3/3)
    assert "First" in lines[1]
    assert "Second" in lines[2]
    assert "Third" in lines[3]


def test_export_transactions_csv_filtered_by_year(db_session: Session) -> None:
    """Export with year filter returns only that year's transactions."""
    cat = _make_category(db_session, "user-1", "C")
    sub = _make_subcategory(db_session, "user-1", cat.id, "S")
    transaction_service.create_transaction(
        db_session,
        "user-1",
        TransactionCreate(
            subcategory_id=sub.id,
            value=-1,
            description="2024",
            date=date(2024, 6, 1),
            hangout_id=None,
        ),
    )
    transaction_service.create_transaction(
        db_session,
        "user-1",
        TransactionCreate(
            subcategory_id=sub.id,
            value=-2,
            description="2025",
            date=date(2025, 6, 1),
            hangout_id=None,
        ),
    )
    csv_str = tm_service.export_transactions_csv(db_session, "user-1", year=2025)
    lines = csv_str.strip().split("\n")
    assert len(lines) == 2  # header + 1 row
    assert "2025" in lines[1]
