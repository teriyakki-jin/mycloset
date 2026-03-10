import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class WearLog(Base):
    __tablename__ = "wear_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    garment_id: Mapped[str] = mapped_column(String, ForeignKey("garments.id", ondelete="CASCADE"), nullable=False, index=True)
    worn_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    occasion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    weather_temp_c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weather_condition: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1~5
    memo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
