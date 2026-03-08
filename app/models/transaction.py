import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.hangout import Hangout
    from app.models.subcategory import Subcategory


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    subcategory_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("subcategories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(1024), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    hangout_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("hangouts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    subcategory: Mapped["Subcategory"] = relationship(
        "Subcategory", back_populates="transactions"
    )
    hangout: Mapped["Hangout | None"] = relationship(
        "Hangout", back_populates="transactions"
    )
