"""가상 피팅 서비스: HuggingFace IDM-VTON Space 사용."""
import asyncio
import tempfile
from pathlib import Path

import os

import httpx
from gradio_client import Client, handle_file

from src.config import settings
from src.services.storage_service import storage_service

_HF_SPACE = "yisol/IDM-VTON"


async def run_tryon(person_image_url: str, garment_image_url: str) -> str:
    """
    가상 피팅 실행 후 결과 이미지 URL 반환.
    person_image_url: 사람 사진 URL
    garment_image_url: 옷 이미지 URL (cutout 또는 original)
    returns: MinIO에 저장된 결과 이미지 URL
    """
    # 이미지 다운로드 (임시 파일)
    with tempfile.TemporaryDirectory() as tmpdir:
        person_path, garment_path = await _download_images(
            person_image_url, garment_image_url, tmpdir
        )

        # HF Space 호출 (blocking → thread pool)
        result_path = await asyncio.get_event_loop().run_in_executor(
            None, _call_idm_vton, person_path, garment_path
        )

        # 결과 MinIO 업로드
        with open(result_path, "rb") as f:
            data = f.read()

        url = storage_service.upload_file(data, "image/png", prefix="tryons")
        return url


async def _download_images(
    person_url: str, garment_url: str, tmpdir: str
) -> tuple[str, str]:
    async with httpx.AsyncClient(timeout=30) as client:
        pr = await client.get(person_url)
        pr.raise_for_status()
        gr = await client.get(garment_url)
        gr.raise_for_status()

    person_path = str(Path(tmpdir) / "person.jpg")
    garment_path = str(Path(tmpdir) / "garment.jpg")
    Path(person_path).write_bytes(pr.content)
    Path(garment_path).write_bytes(gr.content)
    return person_path, garment_path


def _call_idm_vton(person_path: str, garment_path: str) -> str:
    """동기 함수 - run_in_executor에서 실행."""
    # HF 토큰을 환경변수로 설정 (gradio_client 2.x는 HUGGING_FACE_HUB_TOKEN 사용)
    if settings.hf_token:
        os.environ["HUGGING_FACE_HUB_TOKEN"] = settings.hf_token
    client = Client(_HF_SPACE)

    result = client.predict(
        dict={
            "background": handle_file(person_path),
            "layers": [],
            "composite": None,
        },
        garm_img=handle_file(garment_path),
        garment_des="clothing item",
        is_checked=True,
        is_checked_crop=False,
        denoise_steps=20,
        seed=42,
        api_name="/tryon",
    )
    # result = (result_image_path, masked_image_path)
    return result[0]
