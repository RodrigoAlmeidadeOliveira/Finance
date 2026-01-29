"""create transactions table for manual cash flow

Revision ID: 0003_create_transactions_table
Revises: 0002_add_catalog_tables
Create Date: 2025-12-23
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

from app.models.transaction import TransactionType, TransactionStatus

# revision identifiers, used by Alembic.
revision = "0003_create_transactions_table"
down_revision = "0002_add_catalog_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types if they don't exist
    transaction_type_enum = sa.Enum(TransactionType, name="transactiontype")
    transaction_type_enum.create(op.get_bind(), checkfirst=True)

    transaction_status_enum = sa.Enum(TransactionStatus, name="transactionstatus")
    transaction_status_enum.create(op.get_bind(), checkfirst=True)

    # Check if table already exists
    from sqlalchemy import inspect
    bind = op.get_bind()
    inspector = inspect(bind)

    if "transactions" not in inspector.get_table_names():
        op.create_table(
            "transactions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),

            # Dates
            sa.Column("event_date", sa.DateTime(), nullable=False, index=True),
            sa.Column("effective_date", sa.DateTime(), nullable=True),

            # Classification
            sa.Column(
                "transaction_type",
                sa.Enum(TransactionType, name="transactiontype", create_type=False),
                nullable=False,
                index=True
            ),
            sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=False, index=True),

            # Financial details
            sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=True),
            sa.Column("credit_card_id", sa.Integer(), sa.ForeignKey("credit_cards.id"), nullable=True),
            sa.Column("amount", sa.Float(), nullable=False),

            # Description
            sa.Column("description", sa.String(length=500), nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),

            # Status
            sa.Column(
                "status",
                sa.Enum(TransactionStatus, name="transactionstatus", create_type=False),
                nullable=False,
                server_default="PENDING",
                index=True
            ),

            # Recurrence
            sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
            sa.Column("recurrence_parent_id", sa.Integer(), sa.ForeignKey("transactions.id"), nullable=True),

            # Metadata
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
                server_onupdate=sa.func.now(),
            ),

            # Soft delete
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
        )

        # Create indexes for common queries
        op.create_index(
            "idx_transactions_user_event_date",
            "transactions",
            ["user_id", "event_date"],
        )
        op.create_index(
            "idx_transactions_user_type_status",
            "transactions",
            ["user_id", "transaction_type", "status"],
        )
        op.create_index(
            "idx_transactions_category",
            "transactions",
            ["category_id", "event_date"],
        )
        op.create_index(
            "idx_transactions_deleted_at",
            "transactions",
            ["deleted_at"],
        )


def downgrade() -> None:
    # Drop indexes
    op.drop_index("idx_transactions_deleted_at", table_name="transactions")
    op.drop_index("idx_transactions_category", table_name="transactions")
    op.drop_index("idx_transactions_user_type_status", table_name="transactions")
    op.drop_index("idx_transactions_user_event_date", table_name="transactions")

    # Drop table
    op.drop_table("transactions")

    # Drop ENUM types
    transaction_status_enum = sa.Enum(TransactionStatus, name="transactionstatus")
    transaction_status_enum.drop(op.get_bind(), checkfirst=True)

    transaction_type_enum = sa.Enum(TransactionType, name="transactiontype")
    transaction_type_enum.drop(op.get_bind(), checkfirst=True)
