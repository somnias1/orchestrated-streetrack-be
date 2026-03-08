"""
Unit tests for Subcategory service. §1.3: CRUD + category ownership checks; 404 when not owned.
"""

from __future__ import annotations

import pytest
from app.schemas.category import CategoryCreate
from app.schemas.subcategory import SubcategoryCreate, SubcategoryUpdate
from app.services import category as category_service
from app.services import subcategory as subcategory_service
from fastapi import HTTPException
from sqlalchemy.orm import Session


def _make_category(db: Session, user_id: str, name: str = "Cat"):
    return category_service.create_category(
        db, user_id, CategoryCreate(name=name, description=None, is_income=False)
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
    cat = _make_category(db_session, "user-1")
    result = subcategory_service.create_subcategory(
        db_session,
        "user-1",
        SubcategoryCreate(
            category_id=cat.id, name="Lunch", description=None, belongs_to_income=True
        ),
    )
    assert result.name == "Lunch"
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
