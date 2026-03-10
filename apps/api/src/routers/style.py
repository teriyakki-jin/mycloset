from dataclasses import asdict
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.models.user import User
from src.services.style_service import build_style_report

router = APIRouter(prefix="/style", tags=["style"])


class StyleReportResponse(BaseModel):
    total_garments: int
    top_colors: list[dict]
    category_distribution: list[dict]
    formality_avg: Optional[float]
    casual_ratio: float
    formal_ratio: float
    unworn_60d_count: int
    top_style_tags: list[str]
    missing_categories: list[str]
    total_wear_logs: int
    most_worn_garment: Optional[dict]
    summary: str


@router.get("/report", response_model=StyleReportResponse)
async def get_style_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = await build_style_report(db, current_user.id)
    data = asdict(report)
    data.pop("unworn_60d", None)  # ID 목록은 응답에서 제외
    return data
