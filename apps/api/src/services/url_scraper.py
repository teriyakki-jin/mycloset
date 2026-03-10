"""쇼핑몰 URL에서 상품 정보를 추출하는 스크레이퍼."""
import re
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup


@dataclass
class ProductInfo:
    name: str
    image_url: str
    brand: str | None = None
    price: int | None = None


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9",
}

_MUSINSA_CDN = "https://image.msscdn.net"


async def scrape_product(url: str) -> ProductInfo:
    hostname = urlparse(url).hostname or ""

    if "musinsa.com" in hostname:
        return await _scrape_musinsa(url)

    # httpx + BeautifulSoup (og 태그 지원 사이트)
    async with httpx.AsyncClient(headers=_HEADERS, follow_redirects=True, timeout=15) as client:
        resp = await client.get(url)
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")
    return _parse_og(soup)


# ── 무신사 전용 (내부 API 직접 호출) ────────────────────────

async def _scrape_musinsa(url: str) -> ProductInfo:
    # URL에서 상품 번호 추출
    m = re.search(r"/products?/(\d+)", url)
    if not m:
        raise ValueError("무신사 상품 URL 형식이 올바르지 않습니다. (예: /products/12345)")
    product_id = m.group(1)

    headers = {
        **_HEADERS,
        "Accept": "application/json",
        "Referer": f"https://www.musinsa.com/products/{product_id}",
        "x-musinsa-platform-type": "musinsa-store-web",
    }

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=15) as client:
        resp = await client.get(
            f"https://goods-detail.musinsa.com/api2/goods/{product_id}"
        )
        if resp.status_code != 200:
            raise ValueError(f"상품을 찾을 수 없습니다. (상품번호: {product_id})")
        body = resp.json()

    data = body.get("data") or {}
    name = data.get("goodsNm") or data.get("goodsNmEng") or "무신사 상품"
    brand = data.get("brand") or None

    # 썸네일 URL (상대경로 → 절대경로)
    thumb = data.get("thumbnailImageUrl") or ""
    if thumb and not thumb.startswith("http"):
        thumb = _MUSINSA_CDN + thumb

    # 없으면 첫 번째 상품 이미지
    if not thumb:
        images = data.get("goodsImages") or []
        if images:
            img_path = images[0].get("imageUrl", "")
            thumb = (_MUSINSA_CDN + img_path) if img_path and not img_path.startswith("http") else img_path

    if not thumb:
        raise ValueError("무신사 상품 이미지를 찾을 수 없습니다.")

    # 가격
    price_data = data.get("price") or {}
    price = price_data.get("salePrice") or price_data.get("price") or None

    return ProductInfo(name=_clean_name(name), image_url=thumb, brand=brand, price=price)


# ── 공통 og 파서 ─────────────────────────────────────────────

def _parse_og(soup: BeautifulSoup) -> ProductInfo:
    name = (
        _og("title", soup)
        or (soup.find("title") and soup.find("title").get_text(strip=True))
        or "상품"
    )
    image = _og("image", soup) or ""

    if not image:
        raise ValueError("이미지를 찾을 수 없습니다. 지원하지 않는 사이트이거나 상품 페이지가 아닙니다.")

    brand = _meta("og:site_name", soup)
    price = _extract_price(soup)
    return ProductInfo(name=_clean_name(name), image_url=_fix_url(image), brand=brand, price=price)


# ── 유틸 ────────────────────────────────────────────────────

def _og(prop: str, soup: BeautifulSoup) -> str | None:
    tag = soup.find("meta", property=f"og:{prop}")
    return tag.get("content") if tag else None


def _meta(name: str, soup: BeautifulSoup) -> str | None:
    tag = soup.find("meta", attrs={"name": name}) or soup.find("meta", property=name)
    return tag.get("content") if tag else None


def _extract_price(soup: BeautifulSoup) -> int | None:
    price_meta = soup.find("meta", property="product:price:amount")
    if price_meta:
        try:
            return int(float(price_meta.get("content", "0")))
        except ValueError:
            pass
    for selector in ["[class*='price']", "[class*='Price']"]:
        tag = soup.select_one(selector)
        if tag:
            digits = re.sub(r"[^\d]", "", tag.get_text(strip=True))
            if digits and len(digits) >= 4:
                return int(digits)
    return None


def _clean_name(name: str) -> str:
    for sep in [" | ", " - ", " :: ", " : "]:
        if sep in name:
            name = name.split(sep)[0]
    return name.strip()


def _fix_url(url: str) -> str:
    if url.startswith("//"):
        return "https:" + url
    return url
