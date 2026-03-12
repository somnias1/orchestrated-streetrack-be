from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.transaction import Transaction


class Subcategory(Base):
    __tablename__ = "subcategories"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    user_id = mapped_column(String(255), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description = mapped_column(String(1024), nullable=True)
    belongs_to_income: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_periodic: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    due_day = mapped_column(Integer, nullable=True)

    category: Mapped["Category"] = relationship("Category", back_populates="subcategories")  # noqa: UP037
    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: UP037
        "Transaction",
        back_populates="subcategory",
        cascade="save-update, merge",
        passive_deletes=True,
    )
