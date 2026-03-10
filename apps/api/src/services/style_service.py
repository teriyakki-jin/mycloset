"""
스타일 분석 서비스

분석 항목:
- 보유 색상 Top N
- 카테고리 분포
- 캐주얼/포멀 비중
- 최근 60일 미착용 옷
- 스타일 키워드 Top 5
- 보완 추천 아이템
"""

from collections import Counter
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.garment import Garment
from src.models.wear_log import WearLog

CATEGORY_KR = {
    "top": "상의",
    "bottom": "하의",
    "outer": "아우터",
    "dress": "원피스",
    "shoes": "신발",
    "bag": "가방",
    "accessory": "액세서리",
    "etc": "기타",
}

# 균형잡힌 옷장을 위해 없으면 추천할 카테고리
RECOMMENDED_CATEGORIES = ["top", "bottom", "outer", "shoes"]


@dataclass
class StyleReport:
    total_garments: int
    top_colors: list[dict]           # [{"color": "#hex", "count": N}]
    category_distribution: list[dict] # [{"category": "상의", "count": N, "pct": 0.3}]
    formality_avg: Optional[float]
    casual_ratio: float               # 0~1
    formal_ratio: float               # 0~1
    unworn_60d: list[str]             # garment id 목록
    unworn_60d_count: int
    top_style_tags: list[str]
    missing_categories: list[str]     # 보완 추천
    total_wear_logs: int
    most_worn_garment: Optional[dict] # {"id": ..., "name": ..., "wear_count": N}
    summary: str


async def build_style_report(db: AsyncSession, user_id: str) -> StyleReport:
    garments_result = await db.execute(
        select(Garment).where(Garment.user_id == user_id, Garment.is_archived == False)
    )
    garments = garments_result.scalars().all()

    logs_result = await db.execute(
        select(WearLog).where(WearLog.user_id == user_id)
    )
    logs = logs_result.scalars().all()

    total = len(garments)
    if total == 0:
        return StyleReport(
            total_garments=0,
            top_colors=[],
            category_distribution=[],
            formality_avg=None,
            casual_ratio=0.0,
            formal_ratio=0.0,
            unworn_60d=[],
            unworn_60d_count=0,
            top_style_tags=[],
            missing_categories=RECOMMENDED_CATEGORIES,
            total_wear_logs=0,
            most_worn_garment=None,
            summary="아직 등록된 옷이 없습니다. 옷을 추가해보세요!",
        )

    # 색상 Top 5
    color_counter: Counter = Counter()
    for g in garments:
        for c in (g.dominant_colors or []):
            color_counter[c] += 1
    top_colors = [{"color": c, "count": n} for c, n in color_counter.most_common(5)]

    # 카테고리 분포
    cat_counter: Counter = Counter(g.category for g in garments if g.category)
    category_distribution = [
        {"category": CATEGORY_KR.get(cat, cat), "key": cat, "count": cnt, "pct": round(cnt / total, 2)}
        for cat, cnt in cat_counter.most_common()
    ]

    # 포멀도 분석
    formality_scores = [g.formality_score for g in garments if g.formality_score is not None]
    formality_avg = round(sum(formality_scores) / len(formality_scores), 2) if formality_scores else None
    casual_ratio = round(sum(1 for s in formality_scores if s < 0.4) / len(formality_scores), 2) if formality_scores else 0.0
    formal_ratio = round(sum(1 for s in formality_scores if s >= 0.6) / len(formality_scores), 2) if formality_scores else 0.0

    # 최근 60일 미착용
    now = datetime.now(timezone.utc)
    threshold_60d = now - timedelta(days=60)
    unworn_60d = [
        g.id for g in garments
        if (g.last_worn_at is None or g.last_worn_at < threshold_60d) and g.wear_count == 0 or
           (g.last_worn_at is not None and g.last_worn_at < threshold_60d)
    ]

    # 스타일 태그 Top 5
    tag_counter: Counter = Counter()
    for g in garments:
        for t in (g.style_tags or []):
            tag_counter[t] += 1
    top_style_tags = [t for t, _ in tag_counter.most_common(5)]

    # 없는 카테고리 (보완 추천)
    owned_cats = set(g.category for g in garments if g.category)
    missing_categories = [CATEGORY_KR.get(c, c) for c in RECOMMENDED_CATEGORIES if c not in owned_cats]

    # 가장 많이 입은 옷
    most_worn = max(garments, key=lambda g: g.wear_count, default=None)
    most_worn_garment = (
        {"id": most_worn.id, "name": most_worn.name, "wear_count": most_worn.wear_count}
        if most_worn and most_worn.wear_count > 0
        else None
    )

    # 요약 텍스트
    summary = _build_summary(total, category_distribution, formality_avg, len(unworn_60d), top_style_tags)

    return StyleReport(
        total_garments=total,
        top_colors=top_colors,
        category_distribution=category_distribution,
        formality_avg=formality_avg,
        casual_ratio=casual_ratio,
        formal_ratio=formal_ratio,
        unworn_60d=unworn_60d,
        unworn_60d_count=len(unworn_60d),
        top_style_tags=top_style_tags,
        missing_categories=missing_categories,
        total_wear_logs=len(logs),
        most_worn_garment=most_worn_garment,
        summary=summary,
    )


def _build_summary(
    total: int,
    category_dist: list[dict],
    formality_avg: Optional[float],
    unworn_count: int,
    style_tags: list[str],
) -> str:
    parts = [f"총 {total}개의 옷을 보유하고 있습니다."]

    if category_dist:
        top_cat = category_dist[0]
        parts.append(f"{top_cat['category']}이 가장 많습니다 ({top_cat['count']}개).")

    if formality_avg is not None:
        if formality_avg < 0.35:
            parts.append("전반적으로 캐주얼한 스타일을 선호합니다.")
        elif formality_avg > 0.65:
            parts.append("전반적으로 포멀한 스타일을 선호합니다.")
        else:
            parts.append("캐주얼과 포멀을 균형 있게 갖추고 있습니다.")

    if style_tags:
        parts.append(f"주요 스타일 키워드: {', '.join(style_tags[:3])}.")

    if unworn_count > 0:
        parts.append(f"최근 60일 동안 {unworn_count}개의 옷을 입지 않았습니다.")

    return " ".join(parts)
