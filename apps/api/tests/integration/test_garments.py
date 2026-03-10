"""옷장 엔드포인트 통합 테스트."""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.garment import Garment


def _make_garment(user_id: str) -> Garment:
    g = MagicMock(spec=Garment)
    g.id = str(uuid.uuid4())
    g.user_id = user_id
    g.name = "테스트 티셔츠"
    g.original_image_url = "http://localhost:9000/originals/test.jpg"
    g.cutout_image_url = None
    g.thumbnail_url = None
    g.processing_status = "done"
    g.category = "top"
    g.subcategory = "반팔"
    g.brand = None
    g.dominant_colors = ["#FFFFFF"]
    g.seasons = ["spring", "summer"]
    g.style_tags = ["캐주얼"]
    g.notes = None
    g.wear_count = 0
    g.last_worn_at = None
    g.is_archived = False
    g.created_at = datetime.now(timezone.utc)
    g.updated_at = datetime.now(timezone.utc)
    return g


class TestListGarments:
    async def test_requires_auth(self, anon_client):
        resp = await anon_client.get("/garments")
        assert resp.status_code == 401

    async def test_returns_list(self, client, test_user, mock_db):
        garment = _make_garment(test_user.id)
        count_result = MagicMock()
        count_result.scalar.return_value = 1
        list_result = MagicMock()
        list_result.scalars.return_value.all.return_value = [garment]

        mock_db.execute = AsyncMock(
            side_effect=[count_result, list_result]
        )

        resp = await client.get("/garments")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert data["total"] == 1


class TestGetGarment:
    async def test_get_existing_garment(self, client, test_user, mock_db):
        garment = _make_garment(test_user.id)
        result = MagicMock()
        result.scalar_one_or_none.return_value = garment
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get(f"/garments/{garment.id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "테스트 티셔츠"

    async def test_get_nonexistent_returns_404(self, client, mock_db):
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/garments/nonexistent-id")
        assert resp.status_code == 404


class TestDeleteGarment:
    async def test_delete_success(self, client, test_user, mock_db):
        garment = _make_garment(test_user.id)
        result = MagicMock()
        result.scalar_one_or_none.return_value = garment
        mock_db.execute = AsyncMock(return_value=result)
        mock_db.delete = AsyncMock()

        with patch("src.routers.garments.storage_service") as mock_storage:
            mock_storage.delete_file = MagicMock()
            resp = await client.delete(f"/garments/{garment.id}")

        assert resp.status_code == 204

    async def test_delete_nonexistent_returns_404(self, client, mock_db):
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.delete("/garments/nonexistent-id")
        assert resp.status_code == 404


class TestUpdateGarment:
    async def test_update_name(self, client, test_user, mock_db):
        garment = _make_garment(test_user.id)
        result = MagicMock()
        result.scalar_one_or_none.return_value = garment
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.patch(
            f"/garments/{garment.id}",
            json={"name": "수정된 이름"},
        )
        assert resp.status_code == 200
