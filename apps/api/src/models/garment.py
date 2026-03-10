import uuid
from datetime import datetime
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Garment(Base):
    __tablename__ = "garments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    original_image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    cutout_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    mask_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # AI 처리 상태: pending | processing | done | failed
    processing_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # 태깅
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    dominant_colors: Mapped[list] = mapped_column(ARRAY(String), nullable=False, default=list)
    seasons: Mapped[list] = mapped_column(ARRAY(String), nullable=False, default=list)
    pattern: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    material: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    formality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    style_tags: Mapped[list] = mapped_column(ARRAY(String), nullable=False, default=list)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 임베딩 (FashionCLIP / CLIP: 512-dim)
    embedding: Mapped[Optional[list]] = mapped_column(Vector(512), nullable=True)

    # 구매 정보
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="KRW")
    purchase_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # 착용 통계
    wear_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_worn_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_archived: Mapped[bool] = mapped_column(nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    processing_jobs: Mapped[list["GarmentProcessingJob"]] = relationship(
        "GarmentProcessingJob", back_populates="garment", cascade="all, delete-orphan"
    )


class GarmentProcessingJob(Base):
    __tablename__ = "garment_processing_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    garment_id: Mapped[str] = mapped_column(
        String, ForeignKey("garments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step: Mapped[str] = mapped_column(String(50), nullable=False)  # background_removal | tagging | embedding
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    garment: Mapped["Garment"] = relationship("Garment", back_populates="processing_jobs")
