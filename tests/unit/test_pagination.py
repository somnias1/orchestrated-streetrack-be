"""Unit tests for pagination envelope helper. TECHSPEC §4.3."""

from __future__ import annotations

from app.schemas.pagination import paginated_read


def test_paginated_read_empty_no_next() -> None:
    r = paginated_read([], total=0, skip=0, limit=50)
    assert r.has_more is False
    assert r.next_skip is None


def test_paginated_read_middle_page() -> None:
    r = paginated_read([1, 2], total=5, skip=0, limit=2)
    assert r.has_more is True
    assert r.next_skip == 2

    r = paginated_read([3, 4], total=5, skip=2, limit=2)
    assert r.has_more is True
    assert r.next_skip == 4

    r = paginated_read([5], total=5, skip=4, limit=2)
    assert r.has_more is False
    assert r.next_skip is None
