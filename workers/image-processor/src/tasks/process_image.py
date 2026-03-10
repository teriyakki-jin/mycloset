import io
import json
import logging
from datetime import datetime, timezone

import httpx
from PIL import Image
from rembg import remove
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings
from src.storage import upload_bytes

logger = logging.getLogger(__name__)

_engine = None
_session_factory = None


def _get_session_factory() -> async_sessionmaker:
    global _engine, _session_factory
    if _session_factory is None:
        _engine = create_async_engine(settings.database_url, echo=False)
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    return _session_factory


async def process_garment_image(ctx: dict, garment_id: str) -> dict:
    """
    의류 이미지 처리 파이프라인:
    1. 원본 이미지 다운로드
    2. rembg 배경 제거
    3. 썸네일 생성
    4. OpenAI Vision 태깅
    5. DB 업데이트
    """
    logger.info("Starting image processing for garment: %s", garment_id)
    factory = _get_session_factory()

    async with factory() as db:
        from src.models.garment import Garment

        result = await db.execute(select(Garment).where(Garment.id == garment_id))
        garment = result.scalar_one_or_none()
        if not garment:
            logger.error("Garment not found: %s", garment_id)
            return {"error": "not_found"}

        try:
            await _update_status(db, garment, "processing")

            # 1. 원본 이미지 다운로드
            image_bytes = await _download_image(garment.original_image_url)

            # 2. 배경 제거
            cutout_bytes, mask_bytes = await _remove_background(image_bytes)
            cutout_url = await upload_bytes(cutout_bytes, "image/png", prefix="cutouts")
            mask_url = await upload_bytes(mask_bytes, "image/png", prefix="masks")

            # 3. 썸네일
            thumbnail_bytes = _make_thumbnail(cutout_bytes, size=(400, 533))
            thumbnail_url = await upload_bytes(thumbnail_bytes, "image/webp", prefix="thumbnails")

            # 4. AI 태깅
            tags = await _tag_with_openai(image_bytes)

            # 5. DB 저장
            garment.cutout_image_url = cutout_url
            garment.mask_image_url = mask_url
            garment.thumbnail_url = thumbnail_url
            garment.processing_status = "done"
            garment.category = tags.get("category")
            garment.subcategory = tags.get("subcategory")
            garment.dominant_colors = tags.get("dominant_colors", [])
            garment.seasons = tags.get("seasons", [])
            garment.style_tags = tags.get("style_tags", [])
            garment.pattern = tags.get("pattern")
            garment.formality_score = tags.get("formality_score")
            garment.ai_confidence = tags.get("confidence", 0.8)
            if not garment.name or garment.name == "새 옷":
                garment.name = tags.get("name", "새 옷")

            await db.commit()
            logger.info("Processing done for garment: %s", garment_id)
            return {"garment_id": garment_id, "status": "done"}

        except Exception as e:
            logger.exception("Processing failed for garment %s: %s", garment_id, e)
            garment.processing_status = "failed"
            await db.commit()
            return {"garment_id": garment_id, "status": "failed", "error": str(e)}


async def _update_status(db: AsyncSession, garment, status: str) -> None:
    garment.processing_status = status
    await db.commit()


async def _download_image(url: str) -> bytes:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.content


async def _remove_background(image_bytes: bytes) -> tuple[bytes, bytes]:
    """rembg로 배경 제거, (cutout_png, mask_png) 반환"""
    # rembg는 동기 함수이므로 별도 스레드에서 실행하는 것이 이상적이나 MVP에서는 직접 호출
    cutout_bytes = remove(image_bytes)

    # mask 추출 (알파 채널)
    img = Image.open(io.BytesIO(cutout_bytes)).convert("RGBA")
    r, g, b, alpha = img.split()
    mask_buf = io.BytesIO()
    alpha.save(mask_buf, format="PNG")

    cutout_buf = io.BytesIO()
    img.save(cutout_buf, format="PNG")

    return cutout_buf.getvalue(), mask_buf.getvalue()


def _make_thumbnail(image_bytes: bytes, size: tuple[int, int]) -> bytes:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    img.thumbnail(size, Image.LANCZOS)

    # 흰 배경으로 합성 후 WebP 저장
    bg = Image.new("RGB", img.size, (255, 255, 255))
    bg.paste(img, mask=img.split()[3])

    buf = io.BytesIO()
    bg.save(buf, format="WEBP", quality=85)
    return buf.getvalue()


async def _tag_with_openai(image_bytes: bytes) -> dict:
    """OpenAI Vision API로 의류 태깅"""
    if not settings.openai_api_key:
        logger.warning("OPENAI_API_KEY not set, skipping AI tagging")
        return {}

    import base64
    b64 = base64.b64encode(image_bytes).decode()

    prompt = """이 의류 이미지를 분석하고 아래 JSON 형식으로만 응답하세요.

{
  "name": "상품명 (예: 화이트 오버핏 티셔츠)",
  "category": "top|bottom|outer|dress|shoes|bag|accessory|etc 중 하나",
  "subcategory": "더 세부 분류 (예: 반팔티, 청바지, 트렌치코트)",
  "dominant_colors": ["#hex1", "#hex2"],
  "seasons": ["spring", "summer", "autumn", "winter 중 해당하는 것들"],
  "style_tags": ["캐주얼", "미니멀" 등 스타일 키워드 최대 3개],
  "pattern": "solid|stripe|check|floral|graphic|animal|etc 중 하나 또는 null",
  "formality_score": 0.0~1.0 (0=매우 캐주얼, 1=포멀),
  "confidence": 0.0~1.0
}"""

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            json={
                "model": "gpt-4o-mini",
                "max_tokens": 300,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "low"}},
                        ],
                    }
                ],
            },
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"].strip()

        # JSON 파싱 (마크다운 코드블록 제거)
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        return json.loads(content)
