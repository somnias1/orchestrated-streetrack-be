"""Subcategories router: list/get/create/update/delete. TECHSPEC §4.3."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth import CurrentUserId
from app.db.session import get_db
from app.schemas.subcategory import SubcategoryCreate, SubcategoryRead, SubcategoryUpdate
from app.services import subcategory as subcategory_service

router = APIRouter(prefix="/subcategories", tags=["subcategories"])


@router.get("/", response_model=list[SubcategoryRead])
def list_subcategories(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    skip: int = 0,
    limit: int = 50,
    belongs_to_income: bool | None = None,
    category_id: uuid.UUID | None = None,
) -> list[SubcategoryRead]:
    """List subcategories. Optional filters: belongs_to_income, category_id."""
    return subcategory_service.list_subcategories(
        db,
        user_id,
        skip=skip,
        limit=limit,
        belongs_to_income=belongs_to_income,
        category_id=category_id,
    )


@router.post("/", response_model=SubcategoryRead, status_code=status.HTTP_201_CREATED)
def create_subcategory(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    body: SubcategoryCreate,
) -> SubcategoryRead:
    """Create a subcategory for the authenticated user (category must be owned)."""
    return subcategory_service.create_subcategory(db, user_id, body)


@router.get("/{subcategory_id}", response_model=SubcategoryRead)
def get_subcategory(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    subcategory_id: uuid.UUID,
) -> SubcategoryRead:
    """Get a subcategory by id (must be owned by the user)."""
    return subcategory_service.get_subcategory(db, user_id, subcategory_id)


@router.patch("/{subcategory_id}", response_model=SubcategoryRead)
def update_subcategory(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    subcategory_id: uuid.UUID,
    body: SubcategoryUpdate,
) -> SubcategoryRead:
    """Update a subcategory (must be owned; category_id change requires category ownership)."""
    return subcategory_service.update_subcategory(db, user_id, subcategory_id, body)


@router.delete("/{subcategory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subcategory(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    subcategory_id: uuid.UUID,
) -> None:
    """Delete a subcategory (must be owned by the user)."""
    subcategory_service.delete_subcategory(db, user_id, subcategory_id)
