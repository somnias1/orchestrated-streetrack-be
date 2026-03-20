"""Hangouts router: list/get/create/update/delete. TECHSPEC §4.3."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth import CurrentUserId
from app.db.session import get_db
from app.schemas.hangout import HangoutCreate, HangoutRead, HangoutUpdate
from app.schemas.pagination import PaginatedRead
from app.services import hangout as hangout_service

router = APIRouter(prefix="/hangouts", tags=["hangouts"])


@router.get("/", response_model=PaginatedRead[HangoutRead])
def list_hangouts(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    skip: int = 0,
    limit: int = 50,
    name: str | None = None,
) -> PaginatedRead[HangoutRead]:
    """List hangouts for the authenticated user. Optional name filter (icontains)."""
    return hangout_service.list_hangouts(db, user_id, skip=skip, limit=limit, name=name)


@router.post("/", response_model=HangoutRead, status_code=status.HTTP_201_CREATED)
def create_hangout(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    body: HangoutCreate,
) -> HangoutRead:
    """Create a hangout for the authenticated user."""
    return hangout_service.create_hangout(db, user_id, body)


@router.get("/{hangout_id}", response_model=HangoutRead)
def get_hangout(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    hangout_id: uuid.UUID,
) -> HangoutRead:
    """Get a hangout by id (must be owned by the user)."""
    return hangout_service.get_hangout(db, user_id, hangout_id)


@router.patch("/{hangout_id}", response_model=HangoutRead)
def update_hangout(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    hangout_id: uuid.UUID,
    body: HangoutUpdate,
) -> HangoutRead:
    """Update a hangout (must be owned by the user)."""
    return hangout_service.update_hangout(db, user_id, hangout_id, body)


@router.delete("/{hangout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hangout(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    hangout_id: uuid.UUID,
) -> None:
    """Delete a hangout (must be owned by the user)."""
    hangout_service.delete_hangout(db, user_id, hangout_id)
