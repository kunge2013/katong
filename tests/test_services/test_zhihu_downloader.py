# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import sys
import pytest
from unittest.mock import patch, MagicMock

from cinegacha.services.zhihu_downloader import (
    ZhihuError,
    ZhihuUrlError,
    ZhihuAuthError,
    ZhihuScrapeError,
    ZhihuDownloader,
    parse_zhihu_url,
    extract_article_text,
    start_browser_login,
)


# ── URL parsing ──────────────────────────────────────────────────────


def test_parse_valid_url():
    """解析合法知乎 URL"""
    col, sec = parse_zhihu_url(
        "https://www.zhihu.com/market/paid_column/123/section/456"
    )
    assert col == 123
    assert sec == 456


def test_parse_url_with_query():
    """解析带 query 参数的 URL"""
    col, sec = parse_zhihu_url(
        "https://www.zhihu.com/market/paid_column/123/section/456?utm_source=xxx"
    )
    assert col == 123
    assert sec == 456


def test_parse_invalid_url_no_match():
    """解析非知乎 URL 抛 ZhihuUrlError"""
    with pytest.raises(ZhihuUrlError):
        parse_zhihu_url("https://example.com/foo")


def test_parse_invalid_url_missing_section():
    """解析缺少 section 的 URL"""
    with pytest.raises(ZhihuUrlError):
        parse_zhihu_url("https://www.zhihu.com/market/paid_column/123")


# ── HTML text extraction ─────────────────────────────────────────────


def test_extract_article_text_with_container():
    """从有 Post-RichTextContainer 的 HTML 提取文本"""
    html = (
        '<html><body><div class="Post-RichTextContainer">'
        "<p>Hello 世界</p><p>第二段</p></div></body></html>"
    )
    text = extract_article_text(html)
    assert "Hello 世界" in text
    assert "第二段" in text


def test_extract_article_text_fallback_to_richtext():
    """回退到 .RichText"""
    html = (
        '<html><body><div class="RichText">'
        "<p>Fallback text</p></div></body></html>"
    )
    text = extract_article_text(html)
    assert "Fallback text" in text


def test_extract_article_text_no_container():
    """无容器时提取整个 body 文本"""
    html = "<html><body><p>Just plain text</p></body></html>"
    text = extract_article_text(html)
    assert "Just plain text" in text


# ── check_login ──────────────────────────────────────────────────────


def _mock_httpx_response(status_code, content_type, json_data=None, text=""):
    """Helper to build a mocked httpx response."""
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.headers = {"content-type": content_type}
    mock_resp.text = text
    if json_data is not None:
        mock_resp.json.return_value = json_data
    return mock_resp


def test_check_login_success(app):
    """登录状态检查 - 成功"""
    mock_resp = _mock_httpx_response(
        200, "application/json", json_data={"id": "abc123", "name": "test"}
    )
    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.return_value = mock_resp
        downloader = ZhihuDownloader(cookie="test-cookie")
        assert downloader.check_login() is True


def test_check_login_401(app):
    """登录状态检查 - 401 返回 False"""
    mock_resp = _mock_httpx_response(401, "text/html", text="unauthorized")
    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.return_value = mock_resp
        downloader = ZhihuDownloader(cookie="expired")
        assert downloader.check_login() is False


def test_check_login_no_cookie(app):
    """无 cookie 时 check_login 返回 False（不抛异常）"""
    mock_resp = _mock_httpx_response(401, "text/html", text="auth needed")
    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.return_value = mock_resp
        downloader = ZhihuDownloader(cookie=None)
        assert downloader.check_login() is False


# ── fetch_section_content ────────────────────────────────────────────


def test_fetch_section_content_json(app):
    """fetch_section_content 从 JSON 响应提取文本"""
    mock_resp = _mock_httpx_response(
        200,
        "application/json",
        json_data={
            "id": 123,
            "content": '<div class="RichText"><p>这是章节内容</p></div>',
        },
    )
    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.return_value = mock_resp
        downloader = ZhihuDownloader(cookie="test")
        text = downloader.fetch_section_content(123)
        assert "这是章节内容" in text


# ── download_column ──────────────────────────────────────────────────


def test_download_column_merges_sections(app):
    """download_column 合并所有章节文本"""
    with patch.object(
        ZhihuDownloader, "fetch_column_info"
    ) as mock_info, patch.object(
        ZhihuDownloader, "fetch_section_content"
    ) as mock_content:
        mock_info.return_value = {
            "title": "测试小说",
            "sections": [
                {"id": 1, "title": "第一章", "url": ""},
                {"id": 2, "title": "第二章", "url": ""},
            ],
        }
        mock_content.side_effect = ["第一章内容", "第二章内容"]
        downloader = ZhihuDownloader(cookie="test")
        result = downloader.download_column(999)

        assert "第一章" in result["full_text"]
        assert "第一章内容" in result["full_text"]
        assert "第二章内容" in result["full_text"]
        assert result["title"] == "测试小说"
        assert len(result["sections"]) == 2


def test_download_column_401_raises(app):
    """download_column 在 401 时抛 ZhihuAuthError"""
    with patch.object(
        ZhihuDownloader,
        "fetch_column_info",
        side_effect=ZhihuAuthError("cookie expired"),
    ):
        downloader = ZhihuDownloader(cookie="expired")
        with pytest.raises(ZhihuAuthError):
            downloader.download_column(999)


# ── start_browser_login ──────────────────────────────────────────────


def test_start_browser_login_no_playwright(app):
    """未安装 playwright 时抛 ZhihuError"""
    with patch.dict(
        sys.modules, {"playwright": None, "playwright.sync_api": None}
    ):
        with pytest.raises(ZhihuError, match="Playwright"):
            start_browser_login()
