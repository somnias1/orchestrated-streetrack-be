"""Hangout Pydantic schemas. TECHSPEC §4.1."""

from __future__ import annotations

import uuid
from datetime import date as date_type

from pydantic import BaseModel, ConfigDict


class HangoutBase(BaseModel):
    name: str
    date: date_type
    description: str | None = None


class HangoutCreate(HangoutBase):
    """Request body for POST /hangouts/."""


class HangoutUpdate(BaseModel):
    name: str | None = None
    date: date_type | None = None
    description: str | None = None


class HangoutRead(HangoutBase):
    """Response for list, get, create, update."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: str | None = None
