"""add wear_logs

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-10

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "wear_logs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("garment_id", sa.String(), nullable=False),
        sa.Column("worn_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("occasion", sa.String(50), nullable=True),
        sa.Column("weather_temp_c", sa.Float(), nullable=True),
        sa.Column("weather_condition", sa.String(50), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("memo", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["garment_id"], ["garments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_wear_logs_user_id", "wear_logs", ["user_id"])
    op.create_index("ix_wear_logs_garment_id", "wear_logs", ["garment_id"])


def downgrade() -> None:
    op.drop_table("wear_logs")
