"""FK RESTRICT: prevent delete category with subcategories, subcategory with transactions

Revision ID: b1c4e8f2a0d3
Revises: fa33b7335fb1
Create Date: 2026-03-11

"""
from collections.abc import Sequence

from alembic import op

revision: str = "b1c4e8f2a0d3"
down_revision: str | None = "fa33b7335fb1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # subcategories.category_id: CASCADE -> RESTRICT
    op.drop_constraint(
        "subcategories_category_id_fkey",
        "subcategories",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "subcategories_category_id_fkey",
        "subcategories",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    # transactions.subcategory_id: CASCADE -> RESTRICT
    op.drop_constraint(
        "transactions_subcategory_id_fkey",
        "transactions",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "transactions_subcategory_id_fkey",
        "transactions",
        "subcategories",
        ["subcategory_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    # Restore CASCADE for both FKs
    op.drop_constraint(
        "subcategories_category_id_fkey",
        "subcategories",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "subcategories_category_id_fkey",
        "subcategories",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "transactions_subcategory_id_fkey",
        "transactions",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "transactions_subcategory_id_fkey",
        "transactions",
        "subcategories",
        ["subcategory_id"],
        ["id"],
        ondelete="CASCADE",
    )
