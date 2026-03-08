"""Category Pydantic schemas. TECHSPEC §4.1."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    name: str
    description: str | None = None
    is_income: bool = False


class CategoryCreate(CategoryBase):
    """Request body for POST /categories/."""


class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_income: bool | None = None


class CategoryRead(CategoryBase):
    """Response for list, get, create, update."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: str | None = None
