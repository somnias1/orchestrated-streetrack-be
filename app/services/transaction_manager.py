"""Transaction manager: import preview and CSV export. TECHSPEC §4.3, Phases 15 & 20."""

from __future__ import annotations

import csv
import io
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import extract

from app.models.category import Category
from app.models.hangout import Hangout
from app.models.subcategory import Subcategory
from app.models.transaction import Transaction
from app.schemas.transaction import (
    TransactionCreate,
    TransactionImportInvalidRow,
    TransactionImportPreview,
    TransactionImportRequest,
)


def _resolve_subcategory_id(
    db: Session, user_id: str, category_name: str, subcategory_name: str
) -> uuid.UUID | None:
    """Subcategory id if category/subcategory names exist and are owned by user; else None."""
    stmt = (
        select(Subcategory.id)
        .join(Category, Subcategory.category_id == Category.id)
        .where(Category.user_id == user_id)
        .where(Category.name == category_name)
        .where(Subcategory.user_id == user_id)
        .where(Subcategory.name == subcategory_name)
    )
    row = db.execute(stmt).first()
    return row[0] if row else None


def _hangout_owned(db: Session, user_id: str, hangout_id: uuid.UUID) -> bool:
    """Return True if hangout exists and is owned by user."""
    hang = db.get(Hangout, hangout_id)
    return hang is not None and hang.user_id == user_id


def preview_import(
    db: Session, user_id: str, request: TransactionImportRequest
) -> TransactionImportPreview:
    """Resolve rows to subcategory/hangout; return normalized transactions and invalid_rows."""
    transactions: list[TransactionCreate] = []
    invalid_rows: list[tuple[int, str]] = []

    for i, row in enumerate(request.rows):
        subcategory_id = _resolve_subcategory_id(
            db, user_id, row.category_name, row.subcategory_name
        )
        if subcategory_id is None:
            invalid_rows.append((i, "Category/subcategory pair not found or not owned"))
            continue
        if row.hangout_id is not None and not _hangout_owned(db, user_id, row.hangout_id):
            invalid_rows.append((i, "Hangout not found or not owned"))
            continue
        transactions.append(
            TransactionCreate(
                subcategory_id=subcategory_id,
                value=row.value,
                description=row.description,
                date=row.date,
                hangout_id=row.hangout_id,
            )
        )

    return TransactionImportPreview(
        transactions=transactions,
        invalid_rows=[
            TransactionImportInvalidRow(row_index=idx, message=msg) for idx, msg in invalid_rows
        ],
    )


def export_transactions_csv(
    db: Session,
    user_id: str,
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
    subcategory_id: uuid.UUID | None = None,
    hangout_id: uuid.UUID | None = None,
) -> str:
    """Return CSV (oldest to newest) for user's transactions with optional filters."""
    stmt = (
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .options(
            joinedload(Transaction.subcategory).joinedload(Subcategory.category),
            joinedload(Transaction.hangout),
        )
    )
    if year is not None:
        stmt = stmt.where(extract("year", Transaction.date) == year)
    if month is not None:
        stmt = stmt.where(extract("month", Transaction.date) == month)
    if day is not None:
        stmt = stmt.where(extract("day", Transaction.date) == day)
    if subcategory_id is not None:
        stmt = stmt.where(Transaction.subcategory_id == subcategory_id)
    if hangout_id is not None:
        stmt = stmt.where(Transaction.hangout_id == hangout_id)
    stmt = stmt.order_by(Transaction.date.asc())
    rows = db.execute(stmt).unique().scalars().all()

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(
        [
            "date",
            "$",
            "value",
            "category_name",
            "subcategory_name",
            "description",
            "hangout_name",
        ]
    )
    for r in rows:
        category_name = (
            r.subcategory.category.name
            if r.subcategory is not None and r.subcategory.category is not None
            else ""
        )
        writer.writerow(
            [
                r.date.strftime("%d/%m/%Y"),
                "$",
                r.value,
                category_name,
                r.subcategory.name if r.subcategory else "",
                r.description,
                r.hangout.name if r.hangout else "",
            ]
        )
    return out.getvalue()
