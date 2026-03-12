from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.subcategory import Subcategory


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id = mapped_column(String(255), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description = mapped_column(String(1024), nullable=True)
    is_income: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    subcategories: Mapped[list["Subcategory"]] = relationship(  # noqa: UP037
        "Subcategory",
        back_populates="category",
        cascade="save-update, merge",
        passive_deletes=True,
    )
