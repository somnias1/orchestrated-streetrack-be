"""Transaction manager router: import preview and CSV export. TECHSPEC §4.3."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.auth import CurrentUserId
from app.db.session import get_db
from app.schemas.transaction import (
    TransactionImportPreview,
    TransactionImportRequest,
)
from app.services import transaction_manager as tm_service

router = APIRouter(prefix="/transaction-manager", tags=["transaction-manager"])


@router.post("/import", response_model=TransactionImportPreview)
def import_preview(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    body: TransactionImportRequest,
) -> TransactionImportPreview:
    """Validate pasted rows against category/subcategory pairs; return payload for bulk create."""
    return tm_service.preview_import(db, user_id, body)


@router.get("/export")
def export_csv(
    db: Annotated[Session, Depends(get_db)],
    user_id: CurrentUserId,
    year: int | None = None,
    month: int | None = Query(None, ge=1, le=12),
    day: int | None = Query(None, ge=1, le=31),
    subcategory_id: uuid.UUID | None = None,
    hangout_id: uuid.UUID | None = None,
) -> Response:
    """Export transactions as CSV (oldest to newest). Same filters as transaction list."""
    content = tm_service.export_transactions_csv(
        db,
        user_id,
        year=year,
        month=month,
        day=day,
        subcategory_id=subcategory_id,
        hangout_id=hangout_id,
    )
    return Response(content=content, media_type="text/csv")
