"""Transaction service: CRUD + subcategory/hangout ownership. TECHSPEC §4.1, §4.3."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.hangout import Hangout
from app.models.subcategory import Subcategory
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate


def list_transactions(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 50,
) -> list[TransactionRead]:
    """Return transactions for user_id, ordered by date desc."""
    stmt = (
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .order_by(Transaction.date.desc())
        .offset(skip)
        .limit(limit)
    )
    rows = db.execute(stmt).scalars().all()
    return [TransactionRead.model_validate(r) for r in rows]


def get_transaction(
    db: Session, user_id: str, transaction_id: uuid.UUID
) -> TransactionRead:
    """Return transaction if found and owned; else 404."""
    row = db.get(Transaction, transaction_id)
    if row is None or row.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    return TransactionRead.model_validate(row)


def _ensure_subcategory_owned(
    db: Session, user_id: str, subcategory_id: uuid.UUID
) -> None:
    """Raise 404 if subcategory does not exist or is not owned by user."""
    sub = db.get(Subcategory, subcategory_id)
    if sub is None or sub.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subcategory not found",
        )


def _ensure_hangout_owned(db: Session, user_id: str, hangout_id: uuid.UUID) -> None:
    """Raise 404 if hangout does not exist or is not owned by user."""
    hang = db.get(Hangout, hangout_id)
    if hang is None or hang.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hangout not found",
        )


def create_transaction(
    db: Session, user_id: str, body: TransactionCreate
) -> TransactionRead:
    """Create transaction; subcategory and optional hangout must be owned. Else 404."""
    _ensure_subcategory_owned(db, user_id, body.subcategory_id)
    if body.hangout_id is not None:
        _ensure_hangout_owned(db, user_id, body.hangout_id)
    row = Transaction(
        user_id=user_id,
        subcategory_id=body.subcategory_id,
        value=body.value,
        description=body.description,
        date=body.date,
        hangout_id=body.hangout_id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return TransactionRead.model_validate(row)


def update_transaction(
    db: Session,
    user_id: str,
    transaction_id: uuid.UUID,
    body: TransactionUpdate,
) -> TransactionRead:
    """Update transaction if owned; subcategory/hangout changes require ownership. Else 404."""
    row = db.get(Transaction, transaction_id)
    if row is None or row.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    if body.subcategory_id is not None:
        _ensure_subcategory_owned(db, user_id, body.subcategory_id)
        row.subcategory_id = body.subcategory_id
    if body.value is not None:
        row.value = body.value
    if body.description is not None:
        row.description = body.description
    if body.date is not None:
        row.date = body.date
    if body.hangout_id is not None:
        _ensure_hangout_owned(db, user_id, body.hangout_id)
        row.hangout_id = body.hangout_id
    db.commit()
    db.refresh(row)
    return TransactionRead.model_validate(row)


def delete_transaction(
    db: Session, user_id: str, transaction_id: uuid.UUID
) -> None:
    """Delete transaction if owned; else 404."""
    row = db.get(Transaction, transaction_id)
    if row is None or row.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    db.delete(row)
    db.commit()
