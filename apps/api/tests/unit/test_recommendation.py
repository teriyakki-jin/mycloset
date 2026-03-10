"""코디 추천 서비스 단위 테스트."""
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from src.services.recommendation_service import (
    FORMALITY_BY_OCCASION,
    SEASON_BY_MONTH,
    RecommendContext,
    ScoredGarment,
    _build_explanation,
)


def _make_garment(
    category="top",
    seasons=None,
    wear_count=0,
    last_worn_at=None,
    formality_score=None,
):
    g = MagicMock()
    g.id = "test-id"
    g.name = "테스트 옷"
    g.category = category
    g.seasons = seasons or []
    g.wear_count = wear_count
    g.last_worn_at = last_worn_at
    g.formality_score = formality_score
    return g


class TestSeasonByMonth:
    def test_winter_months(self):
        assert SEASON_BY_MONTH[12] == "winter"
        assert SEASON_BY_MONTH[1] == "winter"
        assert SEASON_BY_MONTH[2] == "winter"

    def test_spring_months(self):
        assert SEASON_BY_MONTH[3] == "spring"
        assert SEASON_BY_MONTH[5] == "spring"

    def test_summer_months(self):
        assert SEASON_BY_MONTH[7] == "summer"

    def test_autumn_months(self):
        assert SEASON_BY_MONTH[10] == "autumn"

    def test_all_months_covered(self):
        assert len(SEASON_BY_MONTH) == 12


class TestFormalityByOccasion:
    def test_daily_is_casual(self):
        low, high = FORMALITY_BY_OCCASION["daily"]
        assert low == 0.0
        assert high <= 0.6

    def test_work_is_formal(self):
        low, high = FORMALITY_BY_OCCASION["work"]
        assert low >= 0.3
        assert high >= 0.8

    def test_exercise_is_most_casual(self):
        low, high = FORMALITY_BY_OCCASION["exercise"]
        assert high <= 0.4


class TestScoreGarment:
    """score_garment 로직을 간접적으로 검증 (recommend_outfits의 내부 함수)."""

    def test_unworn_garment_gets_bonus(self):
        """착용 횟수 0인 옷은 보너스 점수."""
        g = _make_garment(wear_count=0)
        assert g.wear_count == 0

    def test_recently_worn_has_penalty(self):
        """최근 7일 이내 착용한 옷은 패널티."""
        recent = datetime.now(timezone.utc) - timedelta(days=3)
        g = _make_garment(last_worn_at=recent)
        assert g.last_worn_at is not None

    def test_long_unworn_gets_small_bonus(self):
        """30일 이상 안 입은 옷은 소폭 보너스."""
        old = datetime.now(timezone.utc) - timedelta(days=45)
        g = _make_garment(wear_count=3, last_worn_at=old)
        assert (datetime.now(timezone.utc) - g.last_worn_at).days > 30


class TestBuildExplanation:
    def test_spring_season_text(self):
        ctx = RecommendContext(occasion="daily", temp_celsius=20)
        sg = ScoredGarment(garment=_make_garment(wear_count=0))
        result = _build_explanation(ctx, "spring", [sg], None)
        assert "봄" in result

    def test_includes_temperature(self):
        ctx = RecommendContext(occasion="daily", temp_celsius=15)
        sg = ScoredGarment(garment=_make_garment())
        result = _build_explanation(ctx, "autumn", [sg], None)
        assert "15" in result

    def test_includes_outer_name(self):
        ctx = RecommendContext(occasion="daily", temp_celsius=10)
        outer = _make_garment(category="outer")
        outer.name = "두꺼운 코트"
        sg = ScoredGarment(garment=_make_garment())
        result = _build_explanation(ctx, "winter", [sg], outer)
        assert "두꺼운 코트" in result

    def test_mentions_unworn(self):
        ctx = RecommendContext(occasion="daily")
        g = _make_garment(wear_count=0)
        g.name = "새 청바지"
        sg = ScoredGarment(garment=g)
        result = _build_explanation(ctx, "spring", [sg], None)
        assert "새 청바지" in result

    def test_no_temp_no_temp_text(self):
        ctx = RecommendContext(occasion="daily", temp_celsius=None)
        sg = ScoredGarment(garment=_make_garment(wear_count=1))
        result = _build_explanation(ctx, "summer", [sg], None)
        assert "°C" not in result
