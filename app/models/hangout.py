import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.transaction import Transaction


class Hangout(Base):
    __tablename__ = "hangouts"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="hangout"
    )
