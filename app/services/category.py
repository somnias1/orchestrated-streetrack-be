"""Category service: list/get/create/update/delete scoped by user_id. TECHSPEC §3.2, §4.1."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.subcategory import Subcategory
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.schemas.pagination import PaginatedRead, paginated_read


def list_categories(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    is_income: bool | None = None,
    name: str | None = None,
) -> PaginatedRead[CategoryRead]:
    """Categories for user_id, by name. Filters: is_income, name (icontains)."""
    conditions = [Category.user_id == user_id]
    if is_income is not None:
        conditions.append(Category.is_income == is_income)
    if name is not None:
        conditions.append(Category.name.ilike(f"%{name}%"))
    where_clause = and_(*conditions)

    count_stmt = select(func.count()).select_from(Category).where(where_clause)
    total = int(db.execute(count_stmt).scalar_one())

    stmt = (
        select(Category)
        .where(where_clause)
        .order_by(Category.name)
        .offset(skip)
        .limit(limit)
    )
    rows = db.execute(stmt).scalars().all()
    return paginated_read(
        [CategoryRead.model_validate(r) for r in rows],
        total=total,
        skip=skip,
        limit=limit,
    )


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
