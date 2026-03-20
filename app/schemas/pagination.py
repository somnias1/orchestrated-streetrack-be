"""Shared pagination envelope for list endpoints. TECHSPEC §4.3."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedRead(BaseModel, Generic[T]):
    """Envelope: current page, total matching filters, echoed skip/limit."""

    items: list[T]
    total: int
    skip: int
    limit: int
