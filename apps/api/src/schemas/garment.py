from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GarmentCreateResponse(BaseModel):
    id: str
    user_id: str
    name: str
    original_image_url: str
    cutout_image_url: Optional[str]
    thumbnail_url: Optional[str]
    processing_status: str
    category: Optional[str]
    subcategory: Optional[str]
    brand: Optional[str]
    dominant_colors: list[str]
    seasons: list[str]
    style_tags: list[str]
    notes: Optional[str]
    wear_count: int
    last_worn_at: Optional[datetime]
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GarmentUpdateRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    dominant_colors: Optional[list[str]] = None
    seasons: Optional[list[str]] = None
    style_tags: Optional[list[str]] = None
    notes: Optional[str] = None
    price: Optional[float] = None
    is_archived: Optional[bool] = None


class GarmentListResponse(BaseModel):
    items: list[GarmentCreateResponse]
    total: int
    page: int
    limit: int
