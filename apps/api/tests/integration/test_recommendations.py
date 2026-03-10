"""코디 추천 엔드포인트 통합 테스트."""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.models.garment import Garment


def _make_garment(category: str, user_id: str) -> Garment:
    g = MagicMock(spec=Garment)
    g.id = str(uuid.uuid4())
    g.user_id = user_id
    g.name = f"테스트 {category}"
    g.category = category
    g.seasons = ["spring", "summer", "autumn", "winter"]
    g.formality_score = 0.3
    g.wear_count = 0
    g.last_worn_at = None
    g.processing_status = "done"
    g.is_archived = False
    g.original_image_url = "http://localhost:9000/test.jpg"
    g.cutout_image_url = None
    g.thumbnail_url = None
    g.subcategory = None
    g.brand = None
    g.dominant_colors = []
    g.style_tags = []
    g.notes = None
    g.created_at = datetime.now(timezone.utc)
    g.updated_at = datetime.now(timezone.utc)
    return g


class TestOutfitRecommendation:
    async def test_requires_auth(self, anon_client):
        resp = await anon_client.post(
            "/recommendations/outfit", json={"occasion": "daily"}
        )
        assert resp.status_code == 401

    async def test_returns_outfits_with_top_and_bottom(self, client, test_user, mock_db):
        top = _make_garment("top", test_user.id)
        bottom = _make_garment("bottom", test_user.id)

        result = MagicMock()
        result.scalars.return_value.all.return_value = [top, bottom]
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.post(
            "/recommendations/outfit",
            json={"occasion": "daily", "temp_celsius": 20},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "outfits" in data
        assert len(data["outfits"]) >= 1

    async def test_partial_recommendation_with_top_only(self, client, test_user, mock_db):
        top = _make_garment("top", test_user.id)

        result = MagicMock()
        result.scalars.return_value.all.return_value = [top]
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.post(
            "/recommendations/outfit",
            json={"occasion": "daily"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["outfits"]) >= 1
        assert data["outfits"][0]["top"] is not None
        assert data["outfits"][0]["bottom"] is None

    async def test_empty_closet_returns_empty(self, client, mock_db):
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.post(
            "/recommendations/outfit",
            json={"occasion": "daily"},
        )
        assert resp.status_code == 200
        assert resp.json()["outfits"] == []

    async def test_invalid_occasion_still_works(self, client, mock_db):
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.post(
            "/recommendations/outfit",
            json={"occasion": "unknown_occasion"},
        )
        assert resp.status_code == 200
