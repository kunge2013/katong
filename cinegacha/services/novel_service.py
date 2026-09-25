# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from typing import Optional
from cinegacha import db
from cinegacha.models.novel import Novel
from cinegacha.services.text_cleaner import TextCleaner
from cinegacha.services.settings_service import SettingsService
from cinegacha.services.zhihu_downloader import (
    ZhihuDownloader,
    ZhihuAuthError,
    parse_zhihu_url,
)


class NovelService:
    """小说服务"""

    def __init__(self):
        self.cleaner = TextCleaner()

    def create_novel(
        self,
        name: str,
        text: Optional[str] = None,
        url: Optional[str] = None
    ) -> Novel:
        """
        创建小说 - 当提供 url 且无 text 时自动检测知乎 URL 并下载

        Args:
            name: 小说名称
            text: 小说文本（直接输入）
            url: 小说 URL（从网站抓取）

        Returns:
            Novel: 创建的小说对象
        """
        # [AGC:START] tool=Cc author=fangkun
        if url and not text:
            # 检测是否为知乎 URL
            if "zhihu.com" in url:
                return self.download_from_url(url)
            # 非知乎 URL，仅保存 URL 不下载
            novel = Novel(name=name, original_text="", share_url=url)
            db.session.add(novel)
            db.session.commit()
            return novel
        # [AGC:END]

        novel = Novel(
            name=name,
            original_text=text or "",
            share_url=url or ""
        )

        db.session.add(novel)
        db.session.commit()

        return novel

    def clean_text(self, novel_id: int) -> Novel:
        """
        执行 4 步清洗流水线

        Args:
            novel_id: 小说 ID

        Returns:
            Novel: 更新后的小说对象
        """
        novel = self.get_novel(novel_id)

        if novel is None:
            raise ValueError(f"小说 {novel_id} 不存在")

        # 执行清洗
        result = self.cleaner.clean(novel.original_text)

        # 更新小说
        novel.content = result.text
        novel.is_format_cleaned = int(result.is_format_cleaned)
        novel.is_serial_cleaned = int(result.is_serial_cleaned)
        novel.is_punct_cleaned = int(result.is_punct_cleaned)
        novel.is_shot_cleaned = int(result.is_shot_cleaned)
        novel.word_count = len(result.text)

        db.session.commit()

        return novel

    def get_novel(self, novel_id: int) -> Optional[Novel]:
        """获取小说详情"""
        return db.session.get(Novel, novel_id)

    def list_novels(self, page: int = 1, per_page: int = 20) -> tuple[list[Novel], int]:
        """
        列表分页

        Args:
            page: 页码
            per_page: 每页数量

        Returns:
            tuple: (小说列表, 总数)
        """
        query = db.session.query(Novel).order_by(Novel.created_at.desc())
        total = query.count()
        novels = query.offset((page - 1) * per_page).limit(per_page).all()
        return novels, total

    def update_novel(self, novel_id: int, **kwargs) -> Novel:
        """更新小说"""
        novel = self.get_novel(novel_id)

        if novel is None:
            raise ValueError(f"小说 {novel_id} 不存在")

        for key, value in kwargs.items():
            if hasattr(novel, key):
                setattr(novel, key, value)

        db.session.commit()
        return novel

    def delete_novel(self, novel_id: int) -> bool:
        """删除小说"""
        novel = self.get_novel(novel_id)

        if novel is None:
            return False

        db.session.delete(novel)
        db.session.commit()
        return True

    # [AGC:START] tool=Cc author=fangkun
    def download_from_url(self, url: str, name: Optional[str] = None) -> Novel:
        """从知乎 URL 下载小说并创建记录

        Args:
            url: 知乎付费专栏 URL
            name: 小说名称（可选，默认使用专栏标题）

        Returns:
            Novel: 创建的小说对象

        Raises:
            ZhihuUrlError: URL 格式错误
            ZhihuAuthError: 未登录知乎
            ZhihuScrapeError: 抓取失败
        """
        # 1. 解析 URL（快速失败）
        column_id, _ = parse_zhihu_url(url)

        # 2. 加载知乎 cookie
        settings = SettingsService()
        cookie = settings.get("zhihu_cookie")
        if not cookie:
            raise ZhihuAuthError("未登录知乎，请先在设置页登录")

        # 3. 下载
        downloader = ZhihuDownloader(cookie=cookie)
        result = downloader.download_column(column_id)

        # 4. 创建小说记录
        novel_name = name or result.get("title") or f"知乎专栏_{column_id}"
        novel = Novel(
            name=novel_name,
            original_text=result["full_text"],
            share_url=url,
            word_count=len(result["full_text"]),
        )
        db.session.add(novel)
        db.session.commit()

        # 5. 自动触发 4 步清洗（失败不影响下载）
        try:
            self.clean_text(novel.id)
        except Exception:
            pass

        return novel
    # [AGC:END]
