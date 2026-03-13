"""Subcategory service: CRUD scoped by user_id; category ownership checks. TECHSPEC §4.1, §4.3."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models.category import Category
from app.models.subcategory import Subcategory
from app.models.transaction import Transaction
from app.schemas.subcategory import SubcategoryCreate, SubcategoryRead, SubcategoryUpdate


def _row_to_read(row: Subcategory) -> SubcategoryRead:
    """Build SubcategoryRead with category_id and category_name from row/relationship."""
    return SubcategoryRead(
        id=row.id,
        name=row.name,
        description=row.description,
        belongs_to_income=row.belongs_to_income,
        is_periodic=row.is_periodic,
        due_day=row.due_day,
        user_id=row.user_id,
        category_id=row.category_id,
        category_name=row.category.name if row.category else "",
    )


def list_subcategories(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    belongs_to_income: bool | None = None,
    category_id: uuid.UUID | None = None,
) -> list[SubcategoryRead]:
    """Return subcategories for user_id. Optional filters: belongs_to_income, category_id."""
    stmt = (
        select(Subcategory)
        .where(Subcategory.user_id == user_id)
        .options(joinedload(Subcategory.category))
    )
    if belongs_to_income is not None:
        stmt = stmt.where(Subcategory.belongs_to_income == belongs_to_income)
    if category_id is not None:
        stmt = stmt.where(Subcategory.category_id == category_id)
    stmt = stmt.order_by(Subcategory.name).offset(skip).limit(limit)
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


def _ensure_category_owned(db: Session, user_id: str, category_id: uuid.UUID) -> Category:
    """Return category if it exists and is owned by user; else raise 404."""
    cat = db.get(Category, category_id)
    if cat is None or cat.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    return cat


def _ensure_type_consistency(category: Category, belongs_to_income: bool) -> None:
    """Raise 422 if subcategory belongs_to_income does not match category.is_income."""
    if category.is_income != belongs_to_income:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="subcategory belongs_to_income must match category is_income",
        )


def create_subcategory(db: Session, user_id: str, body: SubcategoryCreate) -> SubcategoryRead:
    """Create subcategory for user_id; category must be owned by user. Else 404."""
    cat = _ensure_category_owned(db, user_id, body.category_id)
    _ensure_type_consistency(cat, body.belongs_to_income)
    row = Subcategory(
        user_id=user_id,
        category_id=body.category_id,
        name=body.name,
        description=body.description,
        belongs_to_income=body.belongs_to_income,
        is_periodic=body.is_periodic,
        due_day=body.due_day,
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
    row = (
        db.execute(
            select(Subcategory)
            .where(Subcategory.id == subcategory_id)
            .options(joinedload(Subcategory.category))
        )
        .unique()
        .scalars()
        .first()
    )
    if row is None or row.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subcategory not found",
        )
    if body.category_id is not None:
        cat = _ensure_category_owned(db, user_id, body.category_id)
        row.category_id = body.category_id
        effective_income = (
            body.belongs_to_income if body.belongs_to_income is not None else row.belongs_to_income
        )
        _ensure_type_consistency(cat, effective_income)
    if body.belongs_to_income is not None:
        cat = row.category
        if cat is None:
            cat = db.get(Category, row.category_id)
        if cat is not None:
            _ensure_type_consistency(cat, body.belongs_to_income)
        row.belongs_to_income = body.belongs_to_income
    if body.name is not None:
        row.name = body.name
    if body.description is not None:
        row.description = body.description
    if body.is_periodic is not None:
        row.is_periodic = body.is_periodic
    if body.due_day is not None:
        row.due_day = body.due_day
    # When is_periodic is true, due_day must be set (either from body or already on row)
    if row.is_periodic and row.due_day is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="due_day is required when is_periodic is true",
        )
    db.commit()
    db.refresh(row)
    return _row_to_read(row)


def delete_subcategory(db: Session, user_id: str, subcategory_id: uuid.UUID) -> None:
    """Delete subcategory if owned; else 404. Fails with 409 if it has transactions."""
    row = db.get(Subcategory, subcategory_id)
    if row is None or row.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subcategory not found",
        )
    has_transactions = (
        db.execute(select(Transaction).where(Transaction.subcategory_id == subcategory_id).limit(1))
        .scalars()
        .first()
        is not None
    )
    if has_transactions:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete subcategory: it has transactions. Remove or reassign them first.",
        )
    try:
        db.delete(row)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete subcategory: it has transactions. Remove or reassign them first.",
        ) from None
