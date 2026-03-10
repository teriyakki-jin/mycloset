from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.models.user import User
from src.schemas.recommendation import OutfitSetResponse, RecommendRequest, RecommendResponse
from src.services.recommendation_service import RecommendContext, recommend_outfits

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/outfit", response_model=RecommendResponse)
async def get_outfit_recommendation(
    body: RecommendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ctx = RecommendContext(
        occasion=body.occasion,
        temp_celsius=body.temp_celsius,
        weather=body.weather,
        month=body.month,
    )
    outfits = await recommend_outfits(db, current_user.id, ctx, n=3)

    return RecommendResponse(
        outfits=[
            OutfitSetResponse(
                top=o.top,
                bottom=o.bottom,
                outer=o.outer,
                score=o.score,
                explanation=o.explanation,
            )
            for o in outfits
        ],
        context=body,
    )
