from typing import Optional

from pydantic import BaseModel

from src.schemas.garment import GarmentCreateResponse


class RecommendRequest(BaseModel):
    occasion: str = "daily"
    temp_celsius: Optional[float] = None
    weather: Optional[str] = None
    month: Optional[int] = None


class OutfitSetResponse(BaseModel):
    top: Optional[GarmentCreateResponse]
    bottom: Optional[GarmentCreateResponse]
    outer: Optional[GarmentCreateResponse]
    score: float
    explanation: str


class RecommendResponse(BaseModel):
    outfits: list[OutfitSetResponse]
    context: RecommendRequest
