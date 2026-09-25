# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import pytest
from cinegacha import db
from cinegacha.services.novel_service import NovelService


@pytest.fixture
def service(app):
    """创建小说服务实例"""
    return NovelService()


def test_create_novel_from_text(service, app):
    """从文本创建小说"""
    with app.app_context():
        novel = service.create_novel(
            name="测试小说",
            text="这是小说内容"
        )

        assert novel.id is not None
        assert novel.name == "测试小说"
        assert novel.original_text == "这是小说内容"
        assert novel.is_format_cleaned == 0


def test_create_novel_from_url(service, app):
    """从 URL 创建小说"""
    with app.app_context():
        novel = service.create_novel(
            name="知乎小说",
            url="https://www.zhihu.com/market/paid_column/123"
        )

        assert novel.share_url.startswith("https://www.zhihu.com")


def test_clean_text(service, app):
    """清洗小说文本"""
    with app.app_context():
        # 创建小说
        novel = service.create_novel(
            name="测试",
            text="小说内容 [连载]\r\n\r\nHello, world!"
        )

        # 执行清洗
        cleaned = service.clean_text(novel.id)

        assert cleaned.is_format_cleaned == 1
        assert cleaned.is_serial_cleaned == 1
        assert cleaned.is_punct_cleaned == 1
        assert "[连载]" not in cleaned.content
        assert "，" in cleaned.content


def test_clean_nonexistent_novel(service, app):
    """清洗不存在的小说"""
    with app.app_context():
        with pytest.raises(ValueError, match="不存在"):
            service.clean_text(99999)


def test_get_novel(service, app):
    """获取小说"""
    with app.app_context():
        novel = service.create_novel(name="测试", text="内容")
        retrieved = service.get_novel(novel.id)

        assert retrieved is not None
        assert retrieved.name == "测试"


def test_list_novels(service, app):
    """列表分页"""
    with app.app_context():
        # 创建多个小说
        for i in range(5):
            service.create_novel(name=f"小说{i}", text=f"内容{i}")

        novels, total = service.list_novels(page=1, per_page=3)

        assert len(novels) == 3
        assert total == 5


def test_update_novel(service, app):
    """更新小说"""
    with app.app_context():
        novel = service.create_novel(name="原始", text="内容")
        updated = service.update_novel(novel.id, name="更新后")

        assert updated.name == "更新后"


def test_delete_novel(service, app):
    """删除小说"""
    with app.app_context():
        novel = service.create_novel(name="测试", text="内容")
        novel_id = novel.id

        result = service.delete_novel(novel_id)
        assert result is True

        # 验证已删除
        retrieved = service.get_novel(novel_id)
        assert retrieved is None
