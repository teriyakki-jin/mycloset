import uuid
from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.models.garment import Garment
from src.models.user import User
from src.models.wear_log import WearLog
from src.schemas.wear_log import WearLogCreateRequest, WearLogResponse

router = APIRouter(prefix="/wear-logs", tags=["wear-logs"])


@router.post("", response_model=WearLogResponse, status_code=status.HTTP_201_CREATED)
async def create_wear_log(
    body: WearLogCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 해당 garment가 현재 유저 소유인지 확인
    result = await db.execute(
        select(Garment).where(Garment.id == body.garment_id, Garment.user_id == current_user.id)
    )
    garment = result.scalar_one_or_none()
    if not garment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Garment not found")

    log = WearLog(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        **body.model_dump(),
    )
    db.add(log)

    # garment 착용 통계 업데이트
    garment.wear_count = (garment.wear_count or 0) + 1
    worn_at_utc = body.worn_at.replace(tzinfo=timezone.utc) if body.worn_at.tzinfo is None else body.worn_at
    if not garment.last_worn_at or garment.last_worn_at < worn_at_utc:
        garment.last_worn_at = worn_at_utc

    await db.flush()
    return log


@router.get("", response_model=list[WearLogResponse])
async def list_wear_logs(
    garment_id: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(WearLog).where(WearLog.user_id == current_user.id)
    if garment_id:
        query = query.where(WearLog.garment_id == garment_id)

    result = await db.execute(query.order_by(WearLog.worn_at.desc()).limit(limit))
    return result.scalars().all()
