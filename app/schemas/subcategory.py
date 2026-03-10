"""Subcategory Pydantic schemas. TECHSPEC §4.1."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, model_validator


def _due_day_range(value: int | None) -> bool:
    """due_day must be 1-31 when present."""
    if value is None:
        return True
    return 1 <= value <= 31


class SubcategoryBase(BaseModel):
    name: str
    description: str | None = None
    belongs_to_income: bool = False
    is_periodic: bool = False
    due_day: int | None = None


class SubcategoryCreate(SubcategoryBase):
    """Request body for POST /subcategories/. Backend checks category ownership."""

    category_id: uuid.UUID

    @model_validator(mode="after")
    def due_day_required_when_periodic(self) -> SubcategoryCreate:
        if self.is_periodic and self.due_day is None:
            msg = "due_day is required when is_periodic is true"
            raise ValueError(msg)
        if self.due_day is not None and not _due_day_range(self.due_day):
            raise ValueError("due_day must be between 1 and 31")
        return self


class SubcategoryUpdate(BaseModel):
    category_id: uuid.UUID | None = None
    name: str | None = None
    description: str | None = None
    belongs_to_income: bool | None = None
    is_periodic: bool | None = None
    due_day: int | None = None

    @model_validator(mode="after")
    def due_day_valid_range(self) -> SubcategoryUpdate:
        if self.due_day is not None and not _due_day_range(self.due_day):
            raise ValueError("due_day must be between 1 and 31")
        return self


class SubcategoryRead(SubcategoryBase):
    """Response for list, get, create, update. Exposes category_id and category_name."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_id: uuid.UUID
    category_name: str
    user_id: str | None = None
