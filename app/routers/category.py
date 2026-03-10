"""Categories router: list/get/create/update/delete. TECHSPEC §4.3."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth import CurrentUserId
from app.db.session import get_db
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services import category as category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryRead])
def list_categories(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    skip: int = 0,
    limit: int = 50,
    is_income: bool | None = None,
) -> list[CategoryRead]:
    """List categories for the authenticated user. Optional filter by is_income."""
    return category_service.list_categories(
        db, user_id, skip=skip, limit=limit, is_income=is_income
    )


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    body: CategoryCreate,
) -> CategoryRead:
    """Create a category for the authenticated user."""
    return category_service.create_category(db, user_id, body)


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    category_id: uuid.UUID,
) -> CategoryRead:
    """Get a category by id (must be owned by the user)."""
    return category_service.get_category(db, user_id, category_id)


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    category_id: uuid.UUID,
    body: CategoryUpdate,
) -> CategoryRead:
    """Update a category (must be owned by the user)."""
    return category_service.update_category(db, user_id, category_id, body)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    category_id: uuid.UUID,
) -> None:
    """Delete a category (must be owned by the user)."""
    category_service.delete_category(db, user_id, category_id)
