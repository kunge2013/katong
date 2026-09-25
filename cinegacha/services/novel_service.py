# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from typing import Optional
from cinegacha import db
from cinegacha.models.novel import Novel
from cinegacha.services.text_cleaner import TextCleaner


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
        创建小说

        Args:
            name: 小说名称
            text: 小说文本（直接输入）
            url: 小说 URL（从网站抓取）

        Returns:
            Novel: 创建的小说对象
        """
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
        return Novel.query.get(novel_id)

    def list_novels(self, page: int = 1, per_page: int = 20) -> tuple[list[Novel], int]:
        """
        列表分页

        Args:
            page: 页码
            per_page: 每页数量

        Returns:
            tuple: (小说列表, 总数)
        """
        query = Novel.query.order_by(Novel.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return pagination.items, pagination.total

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
