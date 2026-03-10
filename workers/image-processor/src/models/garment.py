"""
Worker용 경량 Garment 모델 (API와 동일한 테이블, 필요한 컬럼만 매핑)
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Garment(Base):
    __tablename__ = "garments"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    original_image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    cutout_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    mask_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    processing_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    dominant_colors: Mapped[list] = mapped_column(ARRAY(String), nullable=False, default=list)
    seasons: Mapped[list] = mapped_column(ARRAY(String), nullable=False, default=list)
    style_tags: Mapped[list] = mapped_column(ARRAY(String), nullable=False, default=list)
    pattern: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    formality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
