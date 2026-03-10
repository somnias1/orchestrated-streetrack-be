"""
Unit tests for Subcategory service. §1.3: CRUD + category ownership; 404 when not owned;
periodic expenses (is_periodic, due_day validation, type consistency).
"""

from __future__ import annotations

import pytest
from app.schemas.category import CategoryCreate
from app.schemas.subcategory import SubcategoryCreate, SubcategoryUpdate
from app.services import category as category_service
from app.services import subcategory as subcategory_service
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session


def _make_category(
    db: Session, user_id: str, name: str = "Cat", *, is_income: bool = False
):
    return category_service.create_category(
        db, user_id, CategoryCreate(name=name, description=None, is_income=is_income)
    )


def test_list_subcategories_empty(db_session: Session) -> None:
    """List returns empty when user has no subcategories."""
    result = subcategory_service.list_subcategories(db_session, "user-1")
    assert result == []


def test_list_subcategories_scoped(db_session: Session) -> None:
    """List returns only subcategories for the given user_id."""
    cat_a = _make_category(db_session, "user-a", "CatA")
    cat_b = _make_category(db_session, "user-b", "CatB")
    subcategory_service.create_subcategory(
        db_session,
        "user-a",
        SubcategoryCreate(
            category_id=cat_a.id, name="SubA", description=None, belongs_to_income=False
        ),
    )
    subcategory_service.create_subcategory(
        db_session,
        "user-b",
        SubcategoryCreate(
            category_id=cat_b.id, name="SubB", description=None, belongs_to_income=False
        ),
    )
    list_a = subcategory_service.list_subcategories(db_session, "user-a")
    list_b = subcategory_service.list_subcategories(db_session, "user-b")
    assert len(list_a) == 1 and list_a[0].name == "SubA" and list_a[0].category_name == "CatA"
    assert len(list_b) == 1 and list_b[0].name == "SubB" and list_b[0].category_name == "CatB"


def test_list_subcategories_filter_by_belongs_to_income(db_session: Session) -> None:
    """§1.3: List with belongs_to_income filter returns only matching subcategories."""
    cat_income = _make_category(db_session, "user-1", "IncomeCat", is_income=True)
    cat_expense = _make_category(db_session, "user-1", "ExpenseCat", is_income=False)
    subcategory_service.create_subcategory(
        db_session,
        "user-1",
        SubcategoryCreate(
            category_id=cat_income.id,
            name="IncomeSub",
            description=None,
            belongs_to_income=True,
        ),
    )
    subcategory_service.create_subcategory(
        db_session,
        "user-1",
        SubcategoryCreate(
            category_id=cat_expense.id,
            name="ExpenseSub",
            description=None,
            belongs_to_income=False,
        ),
    )
    income_only = subcategory_service.list_subcategories(
        db_session, "user-1", belongs_to_income=True
    )
    expense_only = subcategory_service.list_subcategories(
        db_session, "user-1", belongs_to_income=False
    )
    assert len(income_only) == 1 and income_only[0].belongs_to_income is True
    assert len(expense_only) == 1 and expense_only[0].belongs_to_income is False


def test_list_subcategories_filter_by_category_id(db_session: Session) -> None:
    """§1.3: List with category_id filter returns only subcategories in that category."""
    cat1 = _make_category(db_session, "user-1", "Cat1")
    cat2 = _make_category(db_session, "user-1", "Cat2")
    subcategory_service.create_subcategory(
        db_session,
        "user-1",
        SubcategoryCreate(
            category_id=cat1.id, name="Sub1", description=None, belongs_to_income=False
        ),
    )
    subcategory_service.create_subcategory(
        db_session,
        "user-1",
        SubcategoryCreate(
            category_id=cat2.id, name="Sub2", description=None, belongs_to_income=False
        ),
    )
    by_cat1 = subcategory_service.list_subcategories(
        db_session, "user-1", category_id=cat1.id
    )
    by_cat2 = subcategory_service.list_subcategories(
        db_session, "user-1", category_id=cat2.id
    )
    assert len(by_cat1) == 1 and by_cat1[0].category_id == cat1.id
    assert len(by_cat2) == 1 and by_cat2[0].category_id == cat2.id


def test_get_subcategory_found(db_session: Session) -> None:
    """Get returns subcategory when found and owned."""
    cat = _make_category(db_session, "user-1")
    created = subcategory_service.create_subcategory(
        db_session,
        "user-1",
        SubcategoryCreate(category_id=cat.id, name="Sub", description="d", belongs_to_income=False),
    )
    got = subcategory_service.get_subcategory(db_session, "user-1", created.id)
    assert got.id == created.id and got.name == "Sub"


def test_get_subcategory_404_when_not_owned(db_session: Session) -> None:
    """Get raises 404 when subcategory exists but belongs to another user."""
    cat = _make_category(db_session, "user-owner")
    created = subcategory_service.create_subcategory(
        db_session,
        "user-owner",
        SubcategoryCreate(
            category_id=cat.id, name="Mine", description=None, belongs_to_income=False
        ),
    )
    with pytest.raises(HTTPException) as exc_info:
        subcategory_service.get_subcategory(db_session, "user-other", created.id)
    assert exc_info.value.status_code == 404


def test_create_subcategory_404_when_category_not_owned(db_session: Session) -> None:
    """Create raises 404 when category belongs to another user."""
    cat = _make_category(db_session, "user-owner")
    with pytest.raises(HTTPException) as exc_info:
        subcategory_service.create_subcategory(
            db_session,
            "user-other",
            SubcategoryCreate(
                category_id=cat.id, name="Sub", description=None, belongs_to_income=False
            ),
        )
    assert exc_info.value.status_code == 404


def test_create_subcategory_success(db_session: Session) -> None:
    """Create persists subcategory when category is owned."""
    cat = _make_category(db_session, "user-1", "Cat", is_income=True)
    result = subcategory_service.create_subcategory(
        db_session,
        "user-1",
        SubcategoryCreate(
            category_id=cat.id, name="Lunch", description=None, belongs_to_income=True
        ),
    )
    assert result.name == "Lunch"
    assert result.category_id == cat.id
    assert result.category_name == "Cat"
    assert result.belongs_to_income is True


def test_update_subcategory_404_when_not_owned(db_session: Session) -> None:
    """Update raises 404 when subcategory belongs to another user."""
    cat = _make_category(db_session, "user-owner")
    created = subcategory_service.create_subcategory(
        db_session,
        "user-owner",
        SubcategoryCreate(
            category_id=cat.id, name="Mine", description=None, belongs_to_income=False
        ),
    )
    with pytest.raises(HTTPException) as exc_info:
        subcategory_service.update_subcategory(
            db_session, "user-other", created.id, SubcategoryUpdate(name="Hacked")
        )
    assert exc_info.value.status_code == 404


def test_update_subcategory_404_when_category_not_owned(db_session: Session) -> None:
    """Update raises 404 when moving to a category owned by another user."""
    cat_own = _make_category(db_session, "user-1", "Own")
    cat_other = _make_category(db_session, "user-other", "Other")
    created = subcategory_service.create_subcategory(
        db_session,
        "user-1",
        SubcategoryCreate(
            category_id=cat_own.id, name="Sub", description=None, belongs_to_income=False
        ),
    )
    with pytest.raises(HTTPException) as exc_info:
        subcategory_service.update_subcategory(
            db_session, "user-1", created.id, SubcategoryUpdate(category_id=cat_other.id)
        )
    assert exc_info.value.status_code == 404


def test_delete_subcategory_success(db_session: Session) -> None:
    """Delete removes subcategory when owned."""
    cat = _make_category(db_session, "user-1")
    created = subcategory_service.create_subcategory(
        db_session,
        "user-1",
        SubcategoryCreate(
            category_id=cat.id, name="ToDelete", description=None, belongs_to_income=False
        ),
    )
    subcategory_service.delete_subcategory(db_session, "user-1", created.id)
    with pytest.raises(HTTPException) as exc_info:
        subcategory_service.get_subcategory(db_session, "user-1", created.id)
    assert exc_info.value.status_code == 404


def test_create_subcategory_periodic_with_due_day_success(db_session: Session) -> None:
    """§1.3: Create with is_periodic=true and valid due_day returns 201 and includes fields."""
    cat = _make_category(db_session, "user-1", is_income=False)
    result = subcategory_service.create_subcategory(
        db_session,
        "user-1",
        SubcategoryCreate(
            category_id=cat.id,
            name="Rent",
            description=None,
            belongs_to_income=False,
            is_periodic=True,
            due_day=15,
        ),
    )
    assert result.is_periodic is True
    assert result.due_day == 15


def test_create_subcategory_periodic_without_due_day_raises_422(db_session: Session) -> None:
    """§1.3: Create with is_periodic=true and missing due_day raises validation error."""
    cat = _make_category(db_session, "user-1", is_income=False)
    with pytest.raises(ValidationError):
        SubcategoryCreate(
            category_id=cat.id,
            name="Rent",
            description=None,
            belongs_to_income=False,
            is_periodic=True,
            due_day=None,
        )


def test_create_subcategory_type_mismatch_raises_422(db_session: Session) -> None:
    """§1.3: Create with belongs_to_income != category.is_income returns 422."""
    cat = _make_category(db_session, "user-1", "ExpenseCat", is_income=False)
    with pytest.raises(HTTPException) as exc_info:
        subcategory_service.create_subcategory(
            db_session,
            "user-1",
            SubcategoryCreate(
                category_id=cat.id,
                name="Wrong",
                description=None,
                belongs_to_income=True,
            ),
        )
    assert exc_info.value.status_code == 422
