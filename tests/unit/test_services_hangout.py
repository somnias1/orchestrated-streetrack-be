"""
Unit tests for Hangout service. §1.3: list/get/create/update/delete scoped; 404 when not owned.
"""

from __future__ import annotations

import uuid
from datetime import date

import pytest
from app.schemas.hangout import HangoutCreate, HangoutUpdate
from app.services import hangout as hangout_service
from fastapi import HTTPException
from sqlalchemy.orm import Session


def test_list_hangouts_empty(db_session: Session) -> None:
    """List returns empty page when user has no hangouts."""
    result = hangout_service.list_hangouts(db_session, "user-1")
    assert result.items == []
    assert result.total == 0


def test_list_hangouts_scoped(db_session: Session) -> None:
    """List returns only hangouts for the given user_id."""
    hangout_service.create_hangout(
        db_session, "user-a", HangoutCreate(name="A", date=date(2025, 1, 1), description=None)
    )
    hangout_service.create_hangout(
        db_session, "user-b", HangoutCreate(name="B", date=date(2025, 1, 2), description=None)
    )
    page_a = hangout_service.list_hangouts(db_session, "user-a")
    page_b = hangout_service.list_hangouts(db_session, "user-b")
    assert len(page_a.items) == 1 and page_a.items[0].name == "A"
    assert page_a.total == 1
    assert len(page_b.items) == 1 and page_b.items[0].name == "B"
    assert page_b.total == 1


def test_get_hangout_found(db_session: Session) -> None:
    """Get returns hangout when found and owned."""
    created = hangout_service.create_hangout(
        db_session, "user-1", HangoutCreate(name="Party", date=date(2025, 2, 1), description="Fun")
    )
    got = hangout_service.get_hangout(db_session, "user-1", created.id)
    assert got.id == created.id and got.name == "Party"


def test_get_hangout_404_when_not_owned(db_session: Session) -> None:
    """Get raises 404 when hangout exists but belongs to another user."""
    created = hangout_service.create_hangout(
        db_session,
        "user-owner",
        HangoutCreate(name="Mine", date=date(2025, 1, 1), description=None),
    )
    with pytest.raises(HTTPException) as exc_info:
        hangout_service.get_hangout(db_session, "user-other", created.id)
    assert exc_info.value.status_code == 404


def test_get_hangout_404_when_not_found(db_session: Session) -> None:
    """Get raises 404 when hangout id does not exist."""
    with pytest.raises(HTTPException) as exc_info:
        hangout_service.get_hangout(db_session, "user-1", uuid.uuid4())
    assert exc_info.value.status_code == 404


def test_create_hangout(db_session: Session) -> None:
    """Create persists hangout with user_id."""
    result = hangout_service.create_hangout(
        db_session,
        "user-1",
        HangoutCreate(name="Trip", date=date(2025, 6, 15), description="Beach"),
    )
    assert result.name == "Trip"
    assert result.user_id == "user-1"
    list_all = hangout_service.list_hangouts(db_session, "user-1")
    assert len(list_all.items) == 1 and list_all.items[0].id == result.id
    assert list_all.total == 1


def test_list_hangouts_filter_by_name_icontains(db_session: Session) -> None:
    """Optional name filter matches hangout name (icontains)."""
    hangout_service.create_hangout(
        db_session,
        "user-1",
        HangoutCreate(name="Summer BBQ", date=date(2025, 7, 1), description=None),
    )
    hangout_service.create_hangout(
        db_session,
        "user-1",
        HangoutCreate(name="Winter hike", date=date(2025, 1, 1), description=None),
    )
    page = hangout_service.list_hangouts(db_session, "user-1", name="bbq")
    assert [h.name for h in page.items] == ["Summer BBQ"]
    assert page.total == 1


def test_update_hangout_success(db_session: Session) -> None:
    """Update modifies hangout when owned."""
    created = hangout_service.create_hangout(
        db_session, "user-1", HangoutCreate(name="Old", date=date(2025, 1, 1), description=None)
    )
    updated = hangout_service.update_hangout(
        db_session,
        "user-1",
        created.id,
        HangoutUpdate(name="New", date=date(2025, 2, 1), description="Updated"),
    )
    assert updated.name == "New" and updated.description == "Updated"


def test_update_hangout_404_when_not_owned(db_session: Session) -> None:
    """Update raises 404 when hangout belongs to another user."""
    created = hangout_service.create_hangout(
        db_session,
        "user-owner",
        HangoutCreate(name="Mine", date=date(2025, 1, 1), description=None),
    )
    with pytest.raises(HTTPException) as exc_info:
        hangout_service.update_hangout(
            db_session, "user-other", created.id, HangoutUpdate(name="Hacked")
        )
    assert exc_info.value.status_code == 404


def test_delete_hangout_success(db_session: Session) -> None:
    """Delete removes hangout when owned."""
    created = hangout_service.create_hangout(
        db_session,
        "user-1",
        HangoutCreate(name="ToDelete", date=date(2025, 1, 1), description=None),
    )
    hangout_service.delete_hangout(db_session, "user-1", created.id)
    with pytest.raises(HTTPException) as exc_info:
        hangout_service.get_hangout(db_session, "user-1", created.id)
    assert exc_info.value.status_code == 404


def test_delete_hangout_404_when_not_owned(db_session: Session) -> None:
    """Delete raises 404 when hangout belongs to another user."""
    created = hangout_service.create_hangout(
        db_session,
        "user-owner",
        HangoutCreate(name="Mine", date=date(2025, 1, 1), description=None),
    )
    with pytest.raises(HTTPException) as exc_info:
        hangout_service.delete_hangout(db_session, "user-other", created.id)
    assert exc_info.value.status_code == 404
