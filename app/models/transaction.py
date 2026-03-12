from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.hangout import Hangout  # noqa: F401
    from app.models.subcategory import Subcategory


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    subcategory_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("subcategories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(1024), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    hangout_id = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("hangouts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_id = mapped_column(String(255), nullable=True, index=True)

    subcategory: Mapped["Subcategory"] = relationship(  # noqa: UP037
        "Subcategory", back_populates="transactions"
    )
    hangout = relationship("Hangout", back_populates="transactions")
