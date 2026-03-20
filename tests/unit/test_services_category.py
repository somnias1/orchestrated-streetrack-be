"""
Unit tests for Category service. §1.3: list/get/create/update/delete scoped; 404 when not owned.
"""

from __future__ import annotations

import uuid

import pytest
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.subcategory import SubcategoryCreate
from app.services import category as category_service
from app.services import subcategory as subcategory_service
from fastapi import HTTPException
from sqlalchemy.orm import Session


def test_list_categories_empty(db_session: Session) -> None:
    """List returns empty page when user has no categories."""
    result = category_service.list_categories(db_session, "user-1")
    assert result.items == []
    assert result.total == 0
    assert result.skip == 0
    assert result.limit == 50
    assert result.has_more is False
    assert result.next_skip is None


def test_list_categories_scoped(db_session: Session) -> None:
    """List returns only categories for the given user_id."""
    category_service.create_category(
        db_session, "user-a", CategoryCreate(name="A", description=None, is_income=False)
    )
    category_service.create_category(
        db_session, "user-b", CategoryCreate(name="B", description=None, is_income=True)
    )
    page_a = category_service.list_categories(db_session, "user-a")
    page_b = category_service.list_categories(db_session, "user-b")
    assert len(page_a.items) == 1
    assert len(page_b.items) == 1
    assert page_a.items[0].name == "A"
    assert page_b.items[0].name == "B"
    assert page_a.total == 1 and page_b.total == 1


def test_list_categories_filter_by_is_income(db_session: Session) -> None:
    """§1.3: List with is_income filter returns only matching categories."""
    category_service.create_category(
        db_session, "user-1", CategoryCreate(name="Income", description=None, is_income=True)
    )
    category_service.create_category(
        db_session, "user-1", CategoryCreate(name="Expense", description=None, is_income=False)
    )
    all_cats = category_service.list_categories(db_session, "user-1")
    assert len(all_cats.items) == 2
    assert all_cats.total == 2
    income_only = category_service.list_categories(db_session, "user-1", is_income=True)
    expense_only = category_service.list_categories(db_session, "user-1", is_income=False)
    assert len(income_only.items) == 1 and income_only.items[0].is_income is True
    assert income_only.total == 1
    assert len(expense_only.items) == 1 and expense_only.items[0].is_income is False
    assert expense_only.total == 1


def test_list_categories_filter_by_name_icontains(db_session: Session) -> None:
    """Optional name filter matches substrings case-insensitively."""
    category_service.create_category(
        db_session, "user-1", CategoryCreate(name="Groceries", description=None, is_income=False)
    )
    category_service.create_category(
        db_session, "user-1", CategoryCreate(name="Salary", description=None, is_income=True)
    )
    page = category_service.list_categories(db_session, "user-1", name="cer")
    assert [c.name for c in page.items] == ["Groceries"]
    assert page.total == 1


def test_list_categories_pagination_total_and_skip(db_session: Session) -> None:
    """total counts all matches; skip/limit slice items."""
    for n in ("A", "B", "C"):
        category_service.create_category(
            db_session, "user-1", CategoryCreate(name=n, description=None, is_income=False)
        )
    p1 = category_service.list_categories(db_session, "user-1", skip=0, limit=2)
    assert len(p1.items) == 2 and p1.total == 3
    assert p1.has_more is True and p1.next_skip == 2
    p2 = category_service.list_categories(db_session, "user-1", skip=2, limit=2)
    assert len(p2.items) == 1 and p2.total == 3
    assert p2.skip == 2 and p2.limit == 2
    assert p2.has_more is False and p2.next_skip is None


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
    assert len(list_all.items) == 1
    assert list_all.items[0].id == result.id
    assert list_all.total == 1


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


def test_delete_category_409_when_has_subcategories(db_session: Session) -> None:
    """Delete raises 409 when category has subcategories."""
    created = category_service.create_category(
        db_session, "user-1", CategoryCreate(name="Parent", description=None, is_income=False)
    )
    subcategory_service.create_subcategory(
        db_session,
        "user-1",
        SubcategoryCreate(
            category_id=created.id, name="Child", description=None, belongs_to_income=False
        ),
    )
    with pytest.raises(HTTPException) as exc_info:
        category_service.delete_category(db_session, "user-1", created.id)
    assert exc_info.value.status_code == 409
    assert "subcategories" in exc_info.value.detail.lower()
