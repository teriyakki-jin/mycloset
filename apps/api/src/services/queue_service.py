import logging

from arq.connections import RedisSettings, create_pool

from src.config import settings

logger = logging.getLogger(__name__)


async def enqueue_image_processing(garment_id: str) -> None:
    try:
        redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
        await redis.enqueue_job("process_garment_image", garment_id)
        await redis.aclose()
    except Exception as e:
        logger.error("Failed to enqueue image processing for %s: %s", garment_id, e)
        # enqueue 실패는 업로드 자체를 막지 않음 — 재시도는 어드민에서 처리
