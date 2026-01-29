"""add catalog tables for categories and institutions

Revision ID: 0002_add_catalog_tables
Revises: 0001_create_import_tables
Create Date: 2025-01-07
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

from app.models.category import CategoryType

# revision identifiers, used by Alembic.
revision = "0002_add_catalog_tables"
down_revision = "0001_create_import_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM type if it doesn't exist
    category_type_enum = sa.Enum(CategoryType, name="categorytype")
    category_type_enum.create(op.get_bind(), checkfirst=True)

    # Check which tables already exist
    from sqlalchemy import inspect
    bind = op.get_bind()
    inspector = inspect(bind)

    if "categories" not in inspector.get_table_names():
        op.create_table(
            "categories",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("type", sa.Enum(CategoryType, name="categorytype", create_type=False), nullable=False),
            sa.Column("parent_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=True),
            sa.Column("color", sa.String(length=20), nullable=True),
            sa.Column("icon", sa.String(length=50), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
                server_onupdate=sa.func.now(),
            ),
            sa.UniqueConstraint("user_id", "name", "parent_id", name="uq_category_per_parent"),
        )

    if "institutions" not in inspector.get_table_names():
        op.create_table(
            "institutions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("account_type", sa.String(length=50), nullable=False),
            sa.Column("partition", sa.String(length=50), nullable=True),
            sa.Column("initial_balance", sa.Float(), nullable=False, server_default="0"),
            sa.Column("current_balance", sa.Float(), nullable=False, server_default="0"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
                server_onupdate=sa.func.now(),
            ),
            sa.UniqueConstraint("user_id", "name", name="uq_institution_per_user"),
        )

    if "investment_types" not in inspector.get_table_names():
        op.create_table(
            "investment_types",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("classification", sa.String(length=50), nullable=True),
            sa.Column("description", sa.String(length=255), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
                server_onupdate=sa.func.now(),
            ),
            sa.UniqueConstraint("name", name="uq_investment_type_name"),
        )

    if "credit_cards" not in inspector.get_table_names():
        op.create_table(
            "credit_cards",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("brand", sa.String(length=50), nullable=True),
            sa.Column("last_four_digits", sa.String(length=4), nullable=True),
            sa.Column("closing_day", sa.Integer(), nullable=True),
            sa.Column("due_day", sa.Integer(), nullable=True),
            sa.Column("limit_amount", sa.Float(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
                server_onupdate=sa.func.now(),
            ),
            sa.UniqueConstraint("user_id", "name", name="uq_credit_card_per_user"),
        )


def downgrade() -> None:
    op.drop_table("credit_cards")
    op.drop_table("investment_types")
    op.drop_table("institutions")
    op.drop_table("categories")

    category_type_enum = sa.Enum(CategoryType, name="categorytype")
    category_type_enum.drop(op.get_bind(), checkfirst=True)
