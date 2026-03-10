import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.models.garment import Garment
from src.models.user import User
from src.schemas.garment import GarmentCreateResponse, GarmentListResponse, GarmentUpdateRequest
from src.services.storage_service import storage_service

router = APIRouter(prefix="/garments", tags=["garments"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


@router.post("/upload", response_model=GarmentCreateResponse, status_code=status.HTTP_201_CREATED)
async def upload_garment(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}",
        )

    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large (max 20MB)")

    image_url = storage_service.upload_file(data, file.content_type, prefix="originals")

    garment = Garment(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=file.filename or "새 옷",
        original_image_url=image_url,
        processing_status="pending",
    )
    db.add(garment)
    await db.flush()

    # TODO: arq worker에 process_garment_image enqueue (Phase 3)

    return garment


@router.get("", response_model=GarmentListResponse)
async def list_garments(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    is_archived: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    base_query = select(Garment).where(
        Garment.user_id == current_user.id,
        Garment.is_archived == is_archived,
    )
    if category:
        base_query = base_query.where(Garment.category == category)

    total_result = await db.execute(select(func.count()).select_from(base_query.subquery()))
    total = total_result.scalar_one()

    items_result = await db.execute(
        base_query.order_by(Garment.created_at.desc()).offset((page - 1) * limit).limit(limit)
    )
    items = items_result.scalars().all()

    return GarmentListResponse(items=list(items), total=total, page=page, limit=limit)


@router.get("/{garment_id}", response_model=GarmentCreateResponse)
async def get_garment(
    garment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Garment).where(Garment.id == garment_id, Garment.user_id == current_user.id)
    )
    garment = result.scalar_one_or_none()
    if not garment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Garment not found")
    return garment


@router.patch("/{garment_id}", response_model=GarmentCreateResponse)
async def update_garment(
    garment_id: str,
    body: GarmentUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Garment).where(Garment.id == garment_id, Garment.user_id == current_user.id)
    )
    garment = result.scalar_one_or_none()
    if not garment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Garment not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(garment, field, value)

    await db.flush()
    return garment


@router.delete("/{garment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_garment(
    garment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Garment).where(Garment.id == garment_id, Garment.user_id == current_user.id)
    )
    garment = result.scalar_one_or_none()
    if not garment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Garment not found")

    await db.delete(garment)
