"""
Unit tests for Category service. §1.3: list/get/create/update/delete scoped; 404 when not owned.
"""

from __future__ import annotations

import uuid

import pytest
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services import category as category_service
from fastapi import HTTPException
from sqlalchemy.orm import Session


def test_list_categories_empty(db_session: Session) -> None:
    """List returns empty list when user has no categories."""
    result = category_service.list_categories(db_session, "user-1")
    assert result == []


def test_list_categories_scoped(db_session: Session) -> None:
    """List returns only categories for the given user_id."""
    category_service.create_category(
        db_session, "user-a", CategoryCreate(name="A", description=None, is_income=False)
    )
    category_service.create_category(
        db_session, "user-b", CategoryCreate(name="B", description=None, is_income=True)
    )
    list_a = category_service.list_categories(db_session, "user-a")
    list_b = category_service.list_categories(db_session, "user-b")
    assert len(list_a) == 1
    assert len(list_b) == 1
    assert list_a[0].name == "A"
    assert list_b[0].name == "B"


def test_list_categories_filter_by_is_income(db_session: Session) -> None:
    """§1.3: List with is_income filter returns only matching categories."""
    category_service.create_category(
        db_session, "user-1", CategoryCreate(name="Income", description=None, is_income=True)
    )
    category_service.create_category(
        db_session, "user-1", CategoryCreate(name="Expense", description=None, is_income=False)
    )
    all_cats = category_service.list_categories(db_session, "user-1")
    assert len(all_cats) == 2
    income_only = category_service.list_categories(
        db_session, "user-1", is_income=True
    )
    expense_only = category_service.list_categories(
        db_session, "user-1", is_income=False
    )
    assert len(income_only) == 1 and income_only[0].is_income is True
    assert len(expense_only) == 1 and expense_only[0].is_income is False


def test_get_category_found(db_session: Session) -> None:
    """Get returns category when found and owned."""
    created = category_service.create_category(
        db_session, "user-1", CategoryCreate(name="Food", description="Meals", is_income=False)
    )
    got = category_service.get_category(db_session, "user-1", created.id)
    assert got.id == created.id
    assert got.name == "Food"
    assert got.description == "Meals"


def test_get_category_404_when_not_owned(db_session: Session) -> None:
    """Get raises 404 when category exists but belongs to another user."""
    created = category_service.create_category(
        db_session, "user-owner", CategoryCreate(name="Mine", description=None, is_income=False)
    )
    with pytest.raises(HTTPException) as exc_info:
        category_service.get_category(db_session, "user-other", created.id)
    assert exc_info.value.status_code == 404


def test_get_category_404_when_not_found(db_session: Session) -> None:
    """Get raises 404 when category id does not exist."""
    with pytest.raises(HTTPException) as exc_info:
        category_service.get_category(db_session, "user-1", uuid.uuid4())
    assert exc_info.value.status_code == 404


def test_create_category(db_session: Session) -> None:
    """Create persists category with user_id."""
    body = CategoryCreate(name="Transport", description="Commute", is_income=False)
    result = category_service.create_category(db_session, "user-1", body)
    assert result.name == "Transport"
    assert result.description == "Commute"
    assert result.user_id == "user-1"
    list_all = category_service.list_categories(db_session, "user-1")
    assert len(list_all) == 1
    assert list_all[0].id == result.id


def test_update_category_success(db_session: Session) -> None:
    """Update modifies category when owned."""
    created = category_service.create_category(
        db_session, "user-1", CategoryCreate(name="Old", description=None, is_income=False)
    )
    updated = category_service.update_category(
        db_session,
        "user-1",
        created.id,
        CategoryUpdate(name="New", description="Updated", is_income=True),
    )
    assert updated.name == "New"
    assert updated.description == "Updated"
    assert updated.is_income is True


def test_update_category_404_when_not_owned(db_session: Session) -> None:
    """Update raises 404 when category belongs to another user."""
    created = category_service.create_category(
        db_session, "user-owner", CategoryCreate(name="Mine", description=None, is_income=False)
    )
    with pytest.raises(HTTPException) as exc_info:
        category_service.update_category(
            db_session, "user-other", created.id, CategoryUpdate(name="Hacked")
        )
    assert exc_info.value.status_code == 404


def test_delete_category_success(db_session: Session) -> None:
    """Delete removes category when owned."""
    created = category_service.create_category(
        db_session, "user-1", CategoryCreate(name="ToDelete", description=None, is_income=False)
    )
    category_service.delete_category(db_session, "user-1", created.id)
    with pytest.raises(HTTPException) as exc_info:
        category_service.get_category(db_session, "user-1", created.id)
    assert exc_info.value.status_code == 404


def test_delete_category_404_when_not_owned(db_session: Session) -> None:
    """Delete raises 404 when category belongs to another user."""
    created = category_service.create_category(
        db_session, "user-owner", CategoryCreate(name="Mine", description=None, is_income=False)
    )
    with pytest.raises(HTTPException) as exc_info:
        category_service.delete_category(db_session, "user-other", created.id)
    assert exc_info.value.status_code == 404
