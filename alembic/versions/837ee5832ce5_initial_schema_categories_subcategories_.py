"""initial schema categories subcategories transactions hangouts

Revision ID: 837ee5832ce5
Revises:
Create Date: 2026-03-07 19:25:02.887807

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

# revision identifiers, used by Alembic.
revision: str = "837ee5832ce5"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", PG_UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.String(255), nullable=True, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1024), nullable=True),
        sa.Column("is_income", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_table(
        "hangouts",
        sa.Column("id", PG_UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1024), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("user_id", sa.String(255), nullable=True, index=True),
    )
    op.create_table(
        "subcategories",
        sa.Column("id", PG_UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "category_id",
            PG_UUID(as_uuid=True),
            sa.ForeignKey("categories.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("user_id", sa.String(255), nullable=True, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1024), nullable=True),
        sa.Column(
            "belongs_to_income",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.create_table(
        "transactions",
        sa.Column("id", PG_UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "subcategory_id",
            PG_UUID(as_uuid=True),
            sa.ForeignKey("subcategories.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(1024), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column(
            "hangout_id",
            PG_UUID(as_uuid=True),
            sa.ForeignKey("hangouts.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("user_id", sa.String(255), nullable=True, index=True),
    )


def downgrade() -> None:
    op.drop_table("transactions")
    op.drop_table("subcategories")
    op.drop_table("hangouts")
    op.drop_table("categories")
