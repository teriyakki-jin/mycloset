import uuid
from io import BytesIO

import boto3
from botocore.exceptions import ClientError

from src.config import settings

_client = None
_bucket = settings.s3_bucket_name


def _get_client():
    global _client
    if _client is None:
        _client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
        )
        try:
            _client.head_bucket(Bucket=_bucket)
        except ClientError:
            _client.create_bucket(Bucket=_bucket)
    return _client


async def upload_bytes(data: bytes, content_type: str, prefix: str = "files") -> str:
    client = _get_client()
    key = f"{prefix}/{uuid.uuid4()}"
    client.put_object(
        Bucket=_bucket,
        Key=key,
        Body=BytesIO(data),
        ContentType=content_type,
    )
    endpoint = settings.s3_endpoint_url.rstrip("/")
    return f"{endpoint}/{_bucket}/{key}"
