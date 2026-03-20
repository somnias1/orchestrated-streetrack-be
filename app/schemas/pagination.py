"""Shared pagination envelope for list endpoints. TECHSPEC §4.3."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedRead(BaseModel, Generic[T]):
    """Envelope: current page, total matching filters, echoed skip/limit, next-page hints."""

    items: list[T]
    total: int
    skip: int
    limit: int
    has_more: bool
    next_skip: int | None


def paginated_read(
    items: list[T],
    *,
    total: int,
    skip: int,
    limit: int,
) -> PaginatedRead[T]:
    """Build envelope with has_more and next_skip per TECHSPEC §4.3."""
    n = len(items)
    has_more = skip + n < total
    next_skip = (skip + limit) if has_more else None
    return PaginatedRead(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
        next_skip=next_skip,
    )
