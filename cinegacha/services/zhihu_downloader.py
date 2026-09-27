# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

"""
知乎付费专栏下载器
Zhihu paid column downloader.

Unofficial v4 API:
    GET /api/v4/columns/{column_id}/items   — list articles
    GET /api/v4/articles/{article_id}       — article detail (HTML body)
    GET /api/v4/me                          — auth check

Auth: z_c0 cookie required.
"""

from __future__ import annotations

import re
from typing import Any

import httpx
from bs4 import BeautifulSoup


# ── Exceptions ────────────────────────────────────────────────────────


# [AGC:START] tool=Cc author=fangkun
class ZhihuError(Exception):
    """Base exception for Zhihu downloader."""
# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
class ZhihuUrlError(ZhihuError):
    """Invalid URL format."""
# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
class ZhihuAuthError(ZhihuError):
    """Authentication required / cookie expired."""
# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
class ZhihuScrapeError(ZhihuError):
    """Failed to scrape content."""
# [AGC:END]


# ── URL parsing ───────────────────────────────────────────────────────

# [AGC:START] tool=Cc author=fangkun
ZHIHU_URL_PATTERN = re.compile(
    r"zhihu\.com/market/paid_column/(?P<column_id>\d+)/section/(?P<section_id>\d+)"
)


def parse_zhihu_url(url: str) -> tuple[int, int]:
    """解析知乎付费专栏 URL，返回 (column_id, section_id)。

    Args:
        url: 知乎付费专栏链接

    Returns:
        (column_id, section_id)

    Raises:
        ZhihuUrlError: URL 格式不合法
    """
    m = ZHIHU_URL_PATTERN.search(url)
    if not m:
        raise ZhihuUrlError(f"无法解析知乎 URL: {url}")
    return int(m.group("column_id")), int(m.group("section_id"))
# [AGC:END]


# ── HTML text extraction ─────────────────────────────────────────────

# [AGC:START] tool=Cc author=fangkun
def extract_article_text(html: str) -> str:
    """从知乎文章 HTML 中提取纯文本。

    优先选择 .Post-RichTextContainer，其次 .RichText，
    都没有则回退到全文本。

    Args:
        html: 文章 HTML 字符串

    Returns:
        提取后的纯文本
    """
    soup = BeautifulSoup(html, "lxml")
    container = (
        soup.select_one(".Post-RichTextContainer")
        or soup.select_one(".RichText")
    )
    if not container:
        return soup.get_text("\n", strip=True)
    return container.get_text("\n", strip=True)
# [AGC:END]


# ── Downloader class ──────────────────────────────────────────────────

# [AGC:START] tool=Cc author=fangkun
class ZhihuDownloader:
    """知乎付费专栏下载器。

    Attributes:
        BASE_URL: v4 API 基础 URL
    """

    BASE_URL: str = "https://www.zhihu.com/api/v4"

    def __init__(self, cookie: str | None = None, timeout: float = 30.0) -> None:
        """
        Args:
            cookie: z_c0 cookie 值。None 则所有需认证的请求会抛 ZhihuAuthError
            timeout: HTTP 请求超时（秒）
        """
        self._cookie = cookie
        self._timeout = timeout

    # ── internals ──

    def _headers(self) -> dict[str, str]:
        """构造请求头（含 User-Agent / Referer / 可选 Cookie）。"""
        headers: dict[str, str] = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.zhihu.com/",
            "Accept": "application/json, text/plain, */*",
        }
        if self._cookie:
            headers["Cookie"] = f"z_c0={self._cookie}"
        return headers

    def _request(self, path: str) -> dict[str, Any] | str:
        """发送 GET 请求，返回 JSON dict 或纯文本。

        Raises:
            ZhihuAuthError: 401/403
            ZhihuScrapeError: 其他非 200 状态码
        """
        url = f"{self.BASE_URL}{path}"
        with httpx.Client(timeout=self._timeout, follow_redirects=True) as client:
            resp = client.get(url, headers=self._headers())

        if resp.status_code in (401, 403):
            raise ZhihuAuthError(
                f"认证失败 (HTTP {resp.status_code})，cookie 可能已过期"
            )
        if resp.status_code != 200:
            raise ZhihuScrapeError(
                f"请求失败: HTTP {resp.status_code} - {resp.text[:200]}"
            )

        content_type = resp.headers.get("content-type", "")
        if "application/json" in content_type:
            return resp.json()
        return resp.text

    # ── public API ──

    def check_login(self) -> bool:
        """检查登录状态（cookie 是否有效）。

        Returns:
            True 表示已登录，False 表示未登录或 cookie 失效
        """
        try:
            data = self._request("/me")
            return isinstance(data, dict) and "id" in data
        except (ZhihuAuthError, ZhihuScrapeError):
            return False

    def fetch_column_info(self, column_id: int) -> dict[str, Any]:
        """获取专栏信息（标题、章节列表）。

        Args:
            column_id: 专栏 ID

        Returns:
            {"title": str, "sections": [{"id": int, "title": str, "url": str}, ...]}
        """
        data = self._request(
            f"/columns/{column_id}/items?limit=100&offset=0"
        )
        if not isinstance(data, dict):
            raise ZhihuScrapeError("专栏信息返回非 JSON")

        items = data.get("data", [])
        sections = [
            {
                "id": item.get("id"),
                "title": item.get("title", ""),
                "url": item.get("url", ""),
            }
            for item in items
        ]
        return {
            "title": data.get("title", "") if "title" in data else "",
            "sections": sections,
        }

    def fetch_section_content(self, section_id: int) -> str:
        """获取单个章节的文本内容。

        Args:
            section_id: 章节（文章）ID

        Returns:
            章节纯文本
        """
        data = self._request(f"/articles/{section_id}")
        if isinstance(data, dict):
            html = data.get("content", "")
            return extract_article_text(html)
        return extract_article_text(data)

    def download_column(self, column_id: int) -> dict[str, Any]:
        """下载整个专栏的所有章节文本。

        Args:
            column_id: 专栏 ID

        Returns:
            {
                "title": str,
                "sections": [{"id": int, "title": str, "text": str}, ...],
                "full_text": str,
            }
        """
        info = self.fetch_column_info(column_id)
        downloaded_sections: list[dict[str, Any]] = []

        for sec in info["sections"]:
            text = self.fetch_section_content(sec["id"])
            downloaded_sections.append(
                {"id": sec["id"], "title": sec["title"], "text": text}
            )

        full_text = "\n\n".join(
            f"#{s['title']}\n\n{s['text']}"
            for s in downloaded_sections
            if s["text"]
        )
        return {
            "title": info["title"],
            "sections": downloaded_sections,
            "full_text": full_text,
        }
# [AGC:END]


# ── Browser login ─────────────────────────────────────────────────────

# [AGC:START] tool=Cc author=fangkun
def start_browser_login(timeout: int = 300) -> str:
    """启动浏览器让用户扫码登录知乎，返回 z_c0 cookie。

    Args:
        timeout: 等待登录的最大秒数

    Returns:
        z_c0 cookie 值

    Raises:
        ZhihuError: Playwright 未安装
        ZhihuAuthError: 登录成功但未找到 z_c0
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise ZhihuError(
            "Playwright 未安装，请运行: pip install playwright "
            "&& playwright install chromium"
        ) from e

    import os

    # 临时禁用代理（避免系统代理导致 Playwright 连接失败）
    old_no_proxy = os.environ.get("NO_PROXY")
    old_http_proxy = os.environ.get("HTTP_PROXY")
    old_https_proxy = os.environ.get("HTTPS_PROXY")
    os.environ["NO_PROXY"] = "*"
    os.environ.pop("HTTP_PROXY", None)
    os.environ.pop("HTTPS_PROXY", None)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=["--no-proxy-server"])
            try:
                context = browser.new_context()
                page = context.new_page()
                page.goto("https://www.zhihu.com/signin")
                # 等待登录成功：URL 变为知乎首页（可能有也可能没有查询参数）
                page.wait_for_url("**/zhihu.com/**", timeout=timeout * 1000)
                # 额外等待确保 cookie 写入
                import time
                time.sleep(3)
                cookies = context.cookies()
                z_c0 = next(
                    (c["value"] for c in cookies if c["name"] == "z_c0"), None
                )
                if z_c0 is None:
                    raise ZhihuAuthError("登录成功但未找到 z_c0 cookie")
                return z_c0
            finally:
                browser.close()
    finally:
        # 恢复原始代理环境变量
        if old_no_proxy is not None:
            os.environ["NO_PROXY"] = old_no_proxy
        else:
            os.environ.pop("NO_PROXY", None)
        if old_http_proxy is not None:
            os.environ["HTTP_PROXY"] = old_http_proxy
        if old_https_proxy is not None:
            os.environ["HTTPS_PROXY"] = old_https_proxy
# [AGC:END]
