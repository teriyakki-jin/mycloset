import asyncio
import logging
import sys

from arq.connections import RedisSettings

from src.config import settings
from src.tasks.process_image import process_garment_image

logging.basicConfig(level=logging.INFO)

# Windows에서 asyncio ProactorEventLoop 대신 SelectorEventLoop 사용 (Redis 연결 안정성)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class WorkerSettings:
    functions = [process_garment_image]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = 4
    job_timeout = 300  # 5분
