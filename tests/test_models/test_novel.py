# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from cinegacha import db
from cinegacha.models.novel import Novel


def test_create_novel(client):
    """创建小说"""
    novel = Novel(
        name="测试小说",
        original_text="这是原始文本内容"
    )
    db.session.add(novel)
    db.session.commit()

    assert novel.id is not None
    assert novel.name == "测试小说"
    assert novel.original_text == "这是原始文本内容"
    assert novel.is_format_cleaned == 0
    assert novel.created_at is not None


def test_novel_cleaning_flags(client):
    """清洗状态标记"""
    novel = Novel(name="测试", content="内容")
    db.session.add(novel)
    db.session.commit()

    # 默认未清洗
    assert novel.is_format_cleaned == 0
    assert novel.is_serial_cleaned == 0
    assert novel.is_punct_cleaned == 0
    assert novel.is_shot_cleaned == 0

    # 标记清洗完成
    novel.is_format_cleaned = 1
    novel.is_serial_cleaned = 1
    db.session.commit()

    assert novel.is_format_cleaned == 1
    assert novel.is_serial_cleaned == 1


def test_novel_with_url(client):
    """带 URL 的小说"""
    novel = Novel(
        name="知乎小说",
        share_url="https://www.zhihu.com/market/paid_column/123",
        original_text="内容"
    )
    db.session.add(novel)
    db.session.commit()

    assert novel.share_url.startswith("https://www.zhihu.com")
