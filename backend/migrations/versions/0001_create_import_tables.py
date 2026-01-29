"""create import and pending transaction tables

Revision ID: 0001_create_import_tables
Revises:
Create Date: 2025-01-06
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

from app.models.import_batch import ImportStatus
from app.models.pending_transaction import ReviewStatus

# revision identifiers, used by Alembic.
revision = "0001_create_import_tables"
down_revision = "0000"
branch_labels = None
depends_on = None


def _ensure_enum(name: str, enum_cls) -> None:
    """Create the Postgres enum type if it does not exist."""
    values = ", ".join(f"'{member.value}'" for member in enum_cls)
    op.execute(
        sa.text(
            f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_type WHERE typname = '{name}'
                ) THEN
                    CREATE TYPE {name} AS ENUM ({values});
                END IF;
            END
            $$;
            """
        )
    )


def upgrade() -> None:
    # Create ENUM types if they don't exist
    _ensure_enum("importstatus", ImportStatus)
    _ensure_enum("reviewstatus", ReviewStatus)

    # Create tables only if they don't exist
    from sqlalchemy import inspect
    bind = op.get_bind()
    inspector = inspect(bind)

    if "import_batches" not in inspector.get_table_names():
        op.create_table(
            "import_batches",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("filename", sa.String(length=255), nullable=False),
            sa.Column("file_path", sa.String(length=512), nullable=True),
            sa.Column(
                "status",
                sa.Enum(ImportStatus, name="importstatus", create_type=False),
                nullable=False,
                server_default=ImportStatus.PENDING.value,
            ),
            sa.Column("institution_name", sa.String(length=255), nullable=True),
            sa.Column("account_id", sa.String(length=100), nullable=True),
            sa.Column("total_transactions", sa.Integer(), server_default="0"),
            sa.Column("processed_transactions", sa.Integer(), server_default="0"),
            sa.Column("period_start", sa.DateTime(), nullable=True),
            sa.Column("period_end", sa.DateTime(), nullable=True),
            sa.Column("balance", sa.Float(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
                server_onupdate=sa.func.now(),
            ),
            sa.Column("error_message", sa.Text(), nullable=True),
        )

    if "pending_transactions" not in inspector.get_table_names():
        op.create_table(
            "pending_transactions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("import_batch_id", sa.Integer(), sa.ForeignKey("import_batches.id"), nullable=False),
            sa.Column("fitid", sa.String(length=255), nullable=False),
            sa.Column("date", sa.DateTime(), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("amount", sa.Float(), nullable=False),
            sa.Column("transaction_type", sa.String(length=20), nullable=False),
            sa.Column("payee", sa.String(length=255), nullable=True),
            sa.Column("memo", sa.Text(), nullable=True),
            sa.Column("check_number", sa.String(length=50), nullable=True),
            sa.Column("ofx_type", sa.String(length=50), nullable=True),
            sa.Column("predicted_category", sa.String(length=100), nullable=True),
            sa.Column("confidence_score", sa.Float(), nullable=True),
            sa.Column("confidence_level", sa.String(length=20), nullable=True),
            sa.Column("suggested_categories", sa.Text(), nullable=True),
            sa.Column("user_category", sa.String(length=100), nullable=True),
            sa.Column(
                "review_status",
                sa.Enum(ReviewStatus, name="reviewstatus", create_type=False),
                nullable=False,
                server_default=ReviewStatus.PENDING.value,
            ),
            sa.Column("reviewed_at", sa.DateTime(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )

        op.create_index("ix_pending_transactions_fitid", "pending_transactions", ["fitid"])
        op.create_index(
            "ix_pending_transactions_import_batch",
            "pending_transactions",
            ["import_batch_id"],
        )


def downgrade() -> None:
    op.drop_index("ix_pending_transactions_import_batch", table_name="pending_transactions")
    op.drop_index("ix_pending_transactions_fitid", table_name="pending_transactions")
    op.drop_table("pending_transactions")
    op.drop_table("import_batches")

    op.execute(sa.text("DROP TYPE IF EXISTS reviewstatus"))
    op.execute(sa.text("DROP TYPE IF EXISTS importstatus"))
