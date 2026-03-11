"""Transaction Pydantic schemas. TECHSPEC §4.1."""

from __future__ import annotations

import uuid
from datetime import date as date_type

from pydantic import BaseModel, ConfigDict


class TransactionCreate(BaseModel):
    """POST /transactions/ body. Backend checks subcategory and optional hangout ownership."""

    subcategory_id: uuid.UUID
    value: int
    description: str
    date: date_type
    hangout_id: uuid.UUID | None = None


class TransactionBulkCreate(BaseModel):
    """POST /transactions/bulk body. Normalized-ID items; ownership checked then all-or-nothing."""

    transactions: list[TransactionCreate]


class TransactionUpdate(BaseModel):
    subcategory_id: uuid.UUID | None = None
    value: int | None = None
    description: str | None = None
    date: date_type | None = None
    hangout_id: uuid.UUID | None = None


class TransactionRead(BaseModel):
    """Response for list, get, create, update. Exposes ids and names (FE uses ids for lookups)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subcategory_id: uuid.UUID
    subcategory_name: str
    value: int
    description: str
    date: date_type
    hangout_id: uuid.UUID | None = None
    hangout_name: str | None = None
    user_id: str | None = None


# --- Transaction manager import/export (Phase 15, TECHSPEC §4.3) ---


class TransactionImportRow(BaseModel):
    """One pasted sheet row: category/subcategory by name; resolved to IDs server-side."""

    category_name: str
    subcategory_name: str
    value: int
    description: str
    date: date_type
    hangout_id: uuid.UUID | None = None


class TransactionImportRequest(BaseModel):
    """POST /transaction-manager/import body."""

    rows: list[TransactionImportRow]


class TransactionImportInvalidRow(BaseModel):
    """Validation feedback for a row that could not be resolved."""

    row_index: int
    message: str


class TransactionImportPreview(BaseModel):
    """Import preview: payload ready for POST /transactions/bulk + invalid rows."""

    transactions: list[TransactionCreate]
    invalid_rows: list[TransactionImportInvalidRow]
