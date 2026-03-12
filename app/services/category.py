"""Category service: list/get/create/update/delete scoped by user_id. TECHSPEC §3.2, §4.1."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.subcategory import Subcategory
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate


def list_categories(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    is_income: bool | None = None,
) -> list[CategoryRead]:
    """Return categories for user_id, ordered by name. Optional filter by is_income."""
    stmt = select(Category).where(Category.user_id == user_id)
    if is_income is not None:
        stmt = stmt.where(Category.is_income == is_income)
    stmt = stmt.order_by(Category.name).offset(skip).limit(limit)
    rows = db.execute(stmt).scalars().all()
    return [CategoryRead.model_validate(r) for r in rows]


def get_category(db: Session, user_id: str, category_id: uuid.UUID) -> CategoryRead:
    """Return category if found and owned; else 404."""
    row = db.get(Category, category_id)
    if row is None or row.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    return CategoryRead.model_validate(row)


def create_category(db: Session, user_id: str, body: CategoryCreate) -> CategoryRead:
    """Create category for user_id; return CategoryRead."""
    row = Category(
        user_id=user_id,
        name=body.name,
        description=body.description,
        is_income=body.is_income,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return CategoryRead.model_validate(row)


def update_category(
    db: Session,
    user_id: str,
    category_id: uuid.UUID,
    body: CategoryUpdate,
) -> CategoryRead:
    """Update category if owned; else 404."""
    row = db.get(Category, category_id)
    if row is None or row.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    if body.name is not None:
        row.name = body.name
    if body.description is not None:
        row.description = body.description
    if body.is_income is not None:
        row.is_income = body.is_income
    db.commit()
    db.refresh(row)
    return CategoryRead.model_validate(row)


def delete_category(db: Session, user_id: str, category_id: uuid.UUID) -> None:
    """Delete category if owned; else 404. Fails with 409 if it has subcategories."""
    row = db.get(Category, category_id)
    if row is None or row.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    has_subcategories = (
        db.execute(select(Subcategory).where(Subcategory.category_id == category_id).limit(1))
        .scalars()
        .first()
        is not None
    )
    if has_subcategories:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete category: it has subcategories. Remove or reassign them first.",
        )
    try:
        db.delete(row)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete category: it has subcategories. Remove or reassign them first.",
        ) from None
