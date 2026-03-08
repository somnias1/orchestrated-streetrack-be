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


class TransactionUpdate(BaseModel):
    subcategory_id: uuid.UUID | None = None
    value: int | None = None
    description: str | None = None
    date: date_type | None = None
    hangout_id: uuid.UUID | None = None


class TransactionRead(BaseModel):
    """Response for list, get, create, update. Exposes subcategory_name and hangout_name."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subcategory_name: str
    value: int
    description: str
    date: date_type
    hangout_name: str | None = None
    user_id: str | None = None
