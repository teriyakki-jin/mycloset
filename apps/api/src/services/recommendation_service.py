"""
코디 추천 엔진: 규칙 기반 필터 + 점수화

추천 흐름:
1. 하드 필터: 계절, 날씨 온도, 카테고리 보유 여부
2. 점수화: 날씨 적합도 + 상황 적합도 + 안 입은 옷 보너스 + 최근 반복 패널티
3. 코디 조합: 상의 + 하의 + 아우터(선택) 세트 구성
4. 설명 생성
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.garment import Garment

SEASON_BY_MONTH = {
    12: "winter", 1: "winter", 2: "winter",
    3: "spring", 4: "spring", 5: "spring",
    6: "summer", 7: "summer", 8: "summer",
    9: "autumn", 10: "autumn", 11: "autumn",
}

FORMALITY_BY_OCCASION = {
    "daily": (0.0, 0.5),
    "work": (0.4, 0.9),
    "date": (0.3, 0.8),
    "party": (0.5, 1.0),
    "exercise": (0.0, 0.3),
}


@dataclass
class RecommendContext:
    occasion: str = "daily"        # daily | work | date | party | exercise
    temp_celsius: Optional[float] = None
    weather: Optional[str] = None  # clear | rain | snow | cloudy
    month: Optional[int] = None


@dataclass
class ScoredGarment:
    garment: Garment
    score: float = 0.0
    reasons: list[str] = field(default_factory=list)


@dataclass
class OutfitSet:
    top: Optional[Garment]
    bottom: Optional[Garment]
    outer: Optional[Garment]
    score: float
    explanation: str


async def recommend_outfits(
    db: AsyncSession,
    user_id: str,
    ctx: RecommendContext,
    n: int = 3,
) -> list[OutfitSet]:
    current_month = ctx.month or datetime.now(timezone.utc).month
    season = SEASON_BY_MONTH[current_month]

    # 전체 사용 가능한 옷 로드
    result = await db.execute(
        select(Garment).where(
            Garment.user_id == user_id,
            Garment.is_archived == False,
            Garment.processing_status == "done",
        )
    )
    all_garments = result.scalars().all()

    # 카테고리별 분류
    tops = [g for g in all_garments if g.category == "top"]
    bottoms = [g for g in all_garments if g.category == "bottom"]
    outers = [g for g in all_garments if g.category == "outer"]
    dresses = [g for g in all_garments if g.category == "dress"]

    now = datetime.now(timezone.utc)
    recent_threshold = now - timedelta(days=7)

    def score_garment(g: Garment) -> ScoredGarment:
        score = 0.0
        reasons: list[str] = []

        # 계절 적합도 (+30)
        if season in (g.seasons or []):
            score += 30
            reasons.append(f"{season} 시즌 아이템")

        # 날씨/온도 적합도 (+20)
        if ctx.temp_celsius is not None:
            temp = ctx.temp_celsius
            if g.category == "outer":
                if temp < 10:
                    score += 20
                    reasons.append("추운 날씨에 적합한 아우터")
                elif temp < 17:
                    score += 10
            elif g.category in ("top", "dress"):
                if 15 <= temp <= 25:
                    score += 10
                elif temp > 25:
                    score += 5 if "summer" in (g.seasons or []) else 0

        # 상황 적합도 (+20)
        formality_range = FORMALITY_BY_OCCASION.get(ctx.occasion, (0.0, 1.0))
        if g.formality_score is not None:
            low, high = formality_range
            if low <= g.formality_score <= high:
                score += 20
                reasons.append(f"{ctx.occasion} 상황에 어울리는 포멀도")

        # 안 입은 옷 보너스 (+15)
        if g.wear_count == 0:
            score += 15
            reasons.append("아직 한 번도 입지 않은 옷")
        elif g.last_worn_at and g.last_worn_at < now - timedelta(days=30):
            score += 10
            reasons.append("최근에 잘 안 입은 옷")

        # 최근 반복 패널티 (-20)
        if g.last_worn_at and g.last_worn_at > recent_threshold:
            score -= 20

        return ScoredGarment(garment=g, score=score, reasons=reasons)

    scored_tops = sorted([score_garment(g) for g in tops], key=lambda x: x.score, reverse=True)
    scored_bottoms = sorted([score_garment(g) for g in bottoms], key=lambda x: x.score, reverse=True)
    scored_outers = sorted([score_garment(g) for g in outers], key=lambda x: x.score, reverse=True)
    scored_dresses = sorted([score_garment(g) for g in dresses], key=lambda x: x.score, reverse=True)

    outfits: list[OutfitSet] = []
    used_tops: set[str] = set()
    used_bottoms: set[str] = set()

    for i in range(n):
        # 원피스 우선 고려 (짝수 번째)
        if i % 3 == 2 and scored_dresses:
            dress = next((s for s in scored_dresses if s.garment.id not in used_tops), None)
            if dress:
                outer = scored_outers[0].garment if scored_outers and ctx.temp_celsius and ctx.temp_celsius < 17 else None
                explanation = _build_explanation(ctx, season, [dress], outer)
                outfits.append(OutfitSet(
                    top=dress.garment,
                    bottom=None,
                    outer=outer,
                    score=dress.score,
                    explanation=explanation,
                ))
                used_tops.add(dress.garment.id)
                continue

        top = next((s for s in scored_tops if s.garment.id not in used_tops), None)
        bottom = next((s for s in scored_bottoms if s.garment.id not in used_bottoms), None)
        if not top or not bottom:
            break

        needs_outer = ctx.temp_celsius is not None and ctx.temp_celsius < 17
        outer = next(
            (s.garment for s in scored_outers if s.garment.id not in {top.garment.id, bottom.garment.id}),
            None
        ) if needs_outer else None

        total_score = top.score + bottom.score + (scored_outers[0].score if outer else 0)
        explanation = _build_explanation(ctx, season, [top, bottom], outer)

        outfits.append(OutfitSet(
            top=top.garment,
            bottom=bottom.garment,
            outer=outer,
            score=total_score,
            explanation=explanation,
        ))
        used_tops.add(top.garment.id)
        used_bottoms.add(bottom.garment.id)

    return outfits


def _build_explanation(
    ctx: RecommendContext,
    season: str,
    scored: list[ScoredGarment],
    outer: Optional[Garment],
) -> str:
    parts: list[str] = []
    season_kr = {"spring": "봄", "summer": "여름", "autumn": "가을", "winter": "겨울"}[season]
    parts.append(f"{season_kr} 시즌 코디입니다.")

    if ctx.temp_celsius is not None:
        parts.append(f"현재 기온 {ctx.temp_celsius:.0f}°C에 맞게 구성했습니다.")

    if outer:
        parts.append(f"쌀쌀한 날씨를 위해 {outer.name}을(를) 포함했습니다.")

    unworn = [s for s in scored if s.garment.wear_count == 0]
    if unworn:
        names = ", ".join(s.garment.name for s in unworn[:2])
        parts.append(f"아직 입지 않은 {names}을(를) 활용했습니다.")

    return " ".join(parts)
