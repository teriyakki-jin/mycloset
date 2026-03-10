from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WearLogCreateRequest(BaseModel):
    garment_id: str
    worn_at: datetime
    occasion: Optional[str] = None
    weather_temp_c: Optional[float] = None
    weather_condition: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    memo: Optional[str] = None


class WearLogResponse(BaseModel):
    id: str
    garment_id: str
    worn_at: datetime
    occasion: Optional[str]
    weather_temp_c: Optional[float]
    rating: Optional[int]
    memo: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
