"""Subcategory service: CRUD scoped by user_id; category ownership checks. TECHSPEC §4.1, §4.3."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.category import Category
from app.models.subcategory import Subcategory
from app.schemas.subcategory import SubcategoryCreate, SubcategoryRead, SubcategoryUpdate


def _row_to_read(row: Subcategory) -> SubcategoryRead:
    """Build SubcategoryRead with category_name from eager-loaded or lazy-loaded category."""
    return SubcategoryRead(
        id=row.id,
        name=row.name,
        description=row.description,
        belongs_to_income=row.belongs_to_income,
        user_id=row.user_id,
        category_name=row.category.name if row.category else "",
    )


def list_subcategories(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 50,
) -> list[SubcategoryRead]:
    """Return subcategories for user_id, ordered by name."""
    stmt = (
        select(Subcategory)
        .where(Subcategory.user_id == user_id)
        .options(joinedload(Subcategory.category))
        .order_by(Subcategory.name)
        .offset(skip)
        .limit(limit)
    )
    rows = db.execute(stmt).scalars().all()
    return [_row_to_read(r) for r in rows]


def get_subcategory(db: Session, user_id: str, subcategory_id: uuid.UUID) -> SubcategoryRead:
    """Return subcategory if found and owned; else 404."""
    stmt = (
        select(Subcategory)
        .where(Subcategory.id == subcategory_id)
        .options(joinedload(Subcategory.category))
    )
    row = db.execute(stmt).unique().scalars().first()
    if row is None or row.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subcategory not found",
        )
    return _row_to_read(row)


def _ensure_category_owned(db: Session, user_id: str, category_id: uuid.UUID) -> None:
    """Raise 404 if category does not exist or is not owned by user."""
    cat = db.get(Category, category_id)
    if cat is None or cat.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )


def create_subcategory(db: Session, user_id: str, body: SubcategoryCreate) -> SubcategoryRead:
    """Create subcategory for user_id; category must be owned by user. Else 404."""
    _ensure_category_owned(db, user_id, body.category_id)
    row = Subcategory(
        user_id=user_id,
        category_id=body.category_id,
        name=body.name,
        description=body.description,
        belongs_to_income=body.belongs_to_income,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _row_to_read(row)


def update_subcategory(
    db: Session,
    user_id: str,
    subcategory_id: uuid.UUID,
    body: SubcategoryUpdate,
) -> SubcategoryRead:
    """Update subcategory if owned; if category_id is set, that category must be owned. Else 404."""
    row = db.get(Subcategory, subcategory_id)
    if row is None or row.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subcategory not found",
        )
    if body.category_id is not None:
        _ensure_category_owned(db, user_id, body.category_id)
        row.category_id = body.category_id
    if body.name is not None:
        row.name = body.name
    if body.description is not None:
        row.description = body.description
    if body.belongs_to_income is not None:
        row.belongs_to_income = body.belongs_to_income
    db.commit()
    db.refresh(row)
    return _row_to_read(row)


def delete_subcategory(db: Session, user_id: str, subcategory_id: uuid.UUID) -> None:
    """Delete subcategory if owned; else 404."""
    row = db.get(Subcategory, subcategory_id)
    if row is None or row.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subcategory not found",
        )
    db.delete(row)
    db.commit()
