"""initial models

Revision ID: 0001
Revises:
Create Date: 2026-03-10

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "garments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False, server_default=""),
        sa.Column("original_image_url", sa.String(500), nullable=False),
        sa.Column("cutout_image_url", sa.String(500), nullable=True),
        sa.Column("mask_image_url", sa.String(500), nullable=True),
        sa.Column("thumbnail_url", sa.String(500), nullable=True),
        sa.Column("processing_status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("ai_confidence", sa.Float(), nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("subcategory", sa.String(50), nullable=True),
        sa.Column("brand", sa.String(100), nullable=True),
        sa.Column("dominant_colors", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("seasons", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("pattern", sa.String(50), nullable=True),
        sa.Column("material", sa.String(100), nullable=True),
        sa.Column("formality_score", sa.Float(), nullable=True),
        sa.Column("style_tags", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("embedding", Vector(512), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="KRW"),
        sa.Column("purchase_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("wear_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_worn_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_archived", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_garments_user_id", "garments", ["user_id"])

    op.create_table(
        "garment_processing_jobs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("garment_id", sa.String(), nullable=False),
        sa.Column("step", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("payload", postgresql.JSONB(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["garment_id"], ["garments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_garment_processing_jobs_garment_id", "garment_processing_jobs", ["garment_id"])


def downgrade() -> None:
    op.drop_table("garment_processing_jobs")
    op.drop_table("garments")
    op.drop_table("users")
