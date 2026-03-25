"""Transactions router: list/get/create/update/delete. TECHSPEC §4.3."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth import CurrentUserId
from app.db.session import get_db
from app.schemas.pagination import PaginatedRead
from app.schemas.transaction import (
    TransactionBulkCreate,
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)
from app.services import transaction as transaction_service

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/", response_model=PaginatedRead[TransactionRead])
def list_transactions(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    skip: int = 0,
    limit: int = 50,
    year: int | None = None,
    month: int | None = Query(None, ge=1, le=12),
    day: int | None = Query(None, ge=1, le=31),
    subcategory_id: uuid.UUID | None = None,
    hangout_id: uuid.UUID | None = None,
) -> PaginatedRead[TransactionRead]:
    """List transactions (newest first) with pagination envelope. Optional date/id filters."""
    return transaction_service.list_transactions(
        db,
        user_id,
        skip=skip,
        limit=limit,
        year=year,
        month=month,
        day=day,
        subcategory_id=subcategory_id,
        hangout_id=hangout_id,
    )


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    body: TransactionCreate,
) -> TransactionRead:
    """Create a transaction (subcategory and optional hangout must be owned)."""
    return transaction_service.create_transaction(db, user_id, body)


@router.post(
    "/bulk",
    response_model=list[TransactionRead],
    status_code=status.HTTP_201_CREATED,
)
def bulk_create_transactions(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    body: TransactionBulkCreate,
) -> list[TransactionRead]:
    """Create transactions in bulk; ownership checked first, then all-or-nothing."""
    return transaction_service.bulk_create_transactions(db, user_id, body)


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    transaction_id: uuid.UUID,
) -> TransactionRead:
    """Get a transaction by id (must be owned by the user)."""
    return transaction_service.get_transaction(db, user_id, transaction_id)


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    transaction_id: uuid.UUID,
    body: TransactionUpdate,
) -> TransactionRead:
    """Update a transaction (must be owned; subcategory/hangout require ownership)."""
    return transaction_service.update_transaction(db, user_id, transaction_id, body)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    transaction_id: uuid.UUID,
) -> None:
    """Delete a transaction (must be owned by the user)."""
    transaction_service.delete_transaction(db, user_id, transaction_id)
