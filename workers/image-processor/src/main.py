import logging

from arq.connections import RedisSettings

from src.config import settings
from src.tasks.process_image import process_garment_image

logging.basicConfig(level=logging.INFO)


class WorkerSettings:
    functions = [process_garment_image]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = 4
    job_timeout = 300  # 5분
