"""가상 피팅 API."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.models.garment import Garment
from src.models.user import User
from src.services.storage_service import storage_service
from src.services.tryon_service import run_tryon

router = APIRouter(prefix="/tryon", tags=["tryon"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


class TryOnRequest(BaseModel):
    garment_id: str
    person_image_url: str


class TryOnResponse(BaseModel):
    result_url: str


@router.post("", response_model=TryOnResponse)
async def virtual_tryon(
    body: TryOnRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 옷 조회 (본인 소유 확인)
    result = await db.execute(
        select(Garment).where(
            Garment.id == body.garment_id,
            Garment.user_id == current_user.id,
        )
    )
    garment = result.scalar_one_or_none()
    if not garment:
        raise HTTPException(status_code=404, detail="옷을 찾을 수 없습니다.")

    garment_img_url = (
        garment.cutout_image_url
        or garment.original_image_url
    )

    try:
        result_url = await run_tryon(body.person_image_url, garment_img_url)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"가상 피팅 처리 중 오류: {str(e)}")

    return TryOnResponse(result_url=result_url)


@router.post("/upload-person", response_model=dict)
async def upload_person_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """피팅용 사람 사진 업로드 → URL 반환."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="JPG, PNG, WEBP만 업로드 가능합니다.")

    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="파일이 10MB를 초과합니다.")

    url = storage_service.upload_file(data, file.content_type, prefix="person-photos")
    return {"url": url}
