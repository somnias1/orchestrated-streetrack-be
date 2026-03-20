"""Hangout service: list/get/create/update/delete scoped by user_id. TECHSPEC §3.2, §4.1."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.hangout import Hangout
from app.schemas.hangout import HangoutCreate, HangoutRead, HangoutUpdate
from app.schemas.pagination import PaginatedRead


def list_hangouts(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    name: str | None = None,
) -> PaginatedRead[HangoutRead]:
    """Hangouts for user_id, date desc then name. Optional name (icontains)."""
    conditions = [Hangout.user_id == user_id]
    if name is not None:
        conditions.append(Hangout.name.ilike(f"%{name}%"))
    where_clause = and_(*conditions)

    count_stmt = select(func.count()).select_from(Hangout).where(where_clause)
    total = int(db.execute(count_stmt).scalar_one())

    stmt = (
        select(Hangout)
        .where(where_clause)
        .order_by(Hangout.date.desc(), Hangout.name)
        .offset(skip)
        .limit(limit)
    )
    rows = db.execute(stmt).scalars().all()
    return PaginatedRead(
        items=[HangoutRead.model_validate(r) for r in rows],
        total=total,
        skip=skip,
        limit=limit,
    )


def get_hangout(db: Session, user_id: str, hangout_id: uuid.UUID) -> HangoutRead:
    """Return hangout if found and owned; else 404."""
    row = db.get(Hangout, hangout_id)
    if row is None or row.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hangout not found",
        )
    return HangoutRead.model_validate(row)


def create_hangout(db: Session, user_id: str, body: HangoutCreate) -> HangoutRead:
    """Create hangout for user_id; return HangoutRead."""
    row = Hangout(
        user_id=user_id,
        name=body.name,
        description=body.description,
        date=body.date,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return HangoutRead.model_validate(row)


def update_hangout(
    db: Session,
    user_id: str,
    hangout_id: uuid.UUID,
    body: HangoutUpdate,
) -> HangoutRead:
    """Update hangout if owned; else 404."""
    row = db.get(Hangout, hangout_id)
    if row is None or row.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hangout not found",
        )
    if body.name is not None:
        row.name = body.name
    if body.date is not None:
        row.date = body.date
    if body.description is not None:
        row.description = body.description
    db.commit()
    db.refresh(row)
    return HangoutRead.model_validate(row)


def delete_hangout(db: Session, user_id: str, hangout_id: uuid.UUID) -> None:
    """Delete hangout if owned; else 404."""
    row = db.get(Hangout, hangout_id)
    if row is None or row.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hangout not found",
        )
    db.delete(row)
    db.commit()
