"""Subcategory Pydantic schemas. TECHSPEC §4.1."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict


class SubcategoryBase(BaseModel):
    name: str
    description: str | None = None
    belongs_to_income: bool = False


class SubcategoryCreate(SubcategoryBase):
    """Request body for POST /subcategories/. Backend checks category ownership."""

    category_id: uuid.UUID


class SubcategoryUpdate(BaseModel):
    category_id: uuid.UUID | None = None
    name: str | None = None
    description: str | None = None
    belongs_to_income: bool | None = None


class SubcategoryRead(SubcategoryBase):
    """Response for list, get, create, update. Exposes category_name (not category_id)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_name: str
    user_id: str | None = None
