import uuid
from io import BytesIO

import boto3
from botocore.exceptions import ClientError

from src.config import settings


class StorageService:
    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
        )
        self._bucket = settings.s3_bucket_name
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except ClientError:
            self._client.create_bucket(Bucket=self._bucket)

    def upload_file(self, data: bytes, content_type: str, prefix: str = "originals") -> str:
        key = f"{prefix}/{uuid.uuid4()}"
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=BytesIO(data),
            ContentType=content_type,
        )
        return self._build_url(key)

    def _build_url(self, key: str) -> str:
        endpoint = settings.s3_endpoint_url.rstrip("/")
        return f"{endpoint}/{self._bucket}/{key}"

    def delete_file(self, url: str) -> None:
        key = url.split(f"{self._bucket}/", 1)[-1]
        self._client.delete_object(Bucket=self._bucket, Key=key)


storage_service = StorageService()
