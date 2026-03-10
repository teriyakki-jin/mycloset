"""스타일 리포트 엔드포인트 통합 테스트."""
from unittest.mock import AsyncMock, MagicMock

import pytest


class TestStyleReport:
    async def test_requires_auth(self, anon_client):
        resp = await anon_client.get("/style/report")
        assert resp.status_code == 401

    async def test_returns_report_structure(self, client, mock_db):
        # 빈 옷장 결과 mock
        garment_result = MagicMock()
        garment_result.scalars.return_value.all.return_value = []

        wear_log_result = MagicMock()
        wear_log_result.scalar.return_value = 0

        mock_db.execute = AsyncMock(
            side_effect=[garment_result, wear_log_result]
        )

        resp = await client.get("/style/report")
        assert resp.status_code == 200
        data = resp.json()

        # 필수 필드 존재 확인
        required_fields = [
            "total_garments", "top_colors", "category_distribution",
            "formality_avg", "casual_ratio", "formal_ratio",
            "unworn_60d_count", "top_style_tags", "missing_categories",
            "total_wear_logs", "most_worn_garment", "summary",
        ]
        for field in required_fields:
            assert field in data, f"'{field}' 필드가 응답에 없습니다"

    async def test_empty_closet_report(self, client, mock_db):
        garment_result = MagicMock()
        garment_result.scalars.return_value.all.return_value = []
        wear_log_result = MagicMock()
        wear_log_result.scalar.return_value = 0
        mock_db.execute = AsyncMock(
            side_effect=[garment_result, wear_log_result]
        )

        resp = await client.get("/style/report")
        data = resp.json()

        assert data["total_garments"] == 0
        assert data["formality_avg"] is None
        assert data["most_worn_garment"] is None
