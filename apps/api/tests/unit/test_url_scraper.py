"""URL 스크래퍼 단위 테스트."""
import pytest
from bs4 import BeautifulSoup

from src.services.url_scraper import (
    ProductInfo,
    _clean_name,
    _extract_price,
    _fix_url,
    _og,
    _parse_og,
)


class TestCleanName:
    def test_removes_pipe_separator(self):
        assert _clean_name("상품명 | 브랜드") == "상품명"

    def test_removes_dash_separator(self):
        assert _clean_name("상품명 - 쇼핑몰") == "상품명"

    def test_removes_double_colon(self):
        assert _clean_name("상품명 :: 카테고리") == "상품명"

    def test_strips_whitespace(self):
        assert _clean_name("  상품명  ") == "상품명"

    def test_no_separator_unchanged(self):
        assert _clean_name("깔끔한 상품명") == "깔끔한 상품명"


class TestFixUrl:
    def test_protocol_relative_gets_https(self):
        assert _fix_url("//cdn.example.com/img.jpg") == "https://cdn.example.com/img.jpg"

    def test_full_url_unchanged(self):
        assert _fix_url("https://example.com/img.jpg") == "https://example.com/img.jpg"

    def test_http_unchanged(self):
        assert _fix_url("http://example.com/img.jpg") == "http://example.com/img.jpg"


class TestOgParser:
    def _make_soup(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "lxml")

    def test_extracts_og_title(self):
        soup = self._make_soup(
            '<meta property="og:title" content="멋진 티셔츠">'
        )
        assert _og("title", soup) == "멋진 티셔츠"

    def test_returns_none_when_missing(self):
        soup = self._make_soup("<html></html>")
        assert _og("title", soup) is None

    def test_parse_og_raises_without_image(self):
        soup = self._make_soup(
            '<meta property="og:title" content="상품">'
        )
        with pytest.raises(ValueError, match="이미지"):
            _parse_og(soup)

    def test_parse_og_success(self):
        soup = self._make_soup("""
            <meta property="og:title" content="멋진 후드티">
            <meta property="og:image" content="https://example.com/img.jpg">
            <meta property="og:site_name" content="쇼핑몰">
        """)
        result = _parse_og(soup)
        assert isinstance(result, ProductInfo)
        assert result.name == "멋진 후드티"
        assert result.image_url == "https://example.com/img.jpg"
        assert result.brand == "쇼핑몰"


class TestExtractPrice:
    def _make_soup(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "lxml")

    def test_extracts_product_price_meta(self):
        soup = self._make_soup(
            '<meta property="product:price:amount" content="39000">'
        )
        assert _extract_price(soup) == 39000

    def test_returns_none_when_no_price(self):
        soup = self._make_soup("<html></html>")
        assert _extract_price(soup) is None

    def test_extracts_price_from_class(self):
        soup = self._make_soup('<span class="price">39,000원</span>')
        assert _extract_price(soup) == 39000
