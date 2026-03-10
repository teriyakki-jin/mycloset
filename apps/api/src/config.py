from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://closetiq:closetiq_dev@localhost:5432/closetiq"
    database_url_sync: str = "postgresql://closetiq:closetiq_dev@localhost:5432/closetiq"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    jwt_secret_key: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Storage
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin123"
    s3_bucket_name: str = "closetiq-uploads"
    s3_region: str = "us-east-1"

    # AI
    openai_api_key: str = ""


settings = Settings()
