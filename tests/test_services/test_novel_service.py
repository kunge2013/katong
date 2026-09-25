# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import pytest
from unittest.mock import patch
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
    """从 URL 创建小说（非知乎 URL 仅保存）"""
    with app.app_context():
        novel = service.create_novel(
            name="其他小说",
            url="https://example.com/novel/123"
        )

        assert novel.share_url == "https://example.com/novel/123"
        assert novel.original_text == ""


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


def test_create_novel_with_zhihu_url_no_text_auto_downloads(service, app):
    """create_novel 传入知乎 URL 且无 text 时自动下载"""
    with patch('cinegacha.services.novel_service.ZhihuDownloader') as mock_dl_cls, \
         patch('cinegacha.services.novel_service.SettingsService') as mock_settings_cls:
        mock_settings_cls.return_value.get.return_value = "test-cookie"
        mock_dl_cls.return_value.download_column.return_value = {
            "title": "自动下载标题",
            "sections": [],
            "full_text": "自动下载的内容"
        }
        with app.app_context():
            novel = service.create_novel(
                name="Test",
                url="https://www.zhihu.com/market/paid_column/1/section/2"
            )
            assert novel.name == "自动下载标题"
            assert novel.original_text == "自动下载的内容"
            assert novel.share_url == "https://www.zhihu.com/market/paid_column/1/section/2"


def test_create_novel_with_non_zhihu_url_no_download(service, app):
    """create_novel 传入非知乎 URL 且无 text 时仅保存 URL"""
    with app.app_context():
        novel = service.create_novel(
            name="Test",
            url="https://example.com/some/novel"
        )
        assert novel.share_url == "https://example.com/some/novel"
        assert novel.original_text == ""


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


def test_download_from_url_creates_novel(service, app):
    """download_from_url 创建小说"""
    with patch('cinegacha.services.novel_service.ZhihuDownloader') as mock_dl_cls, \
         patch('cinegacha.services.novel_service.SettingsService') as mock_settings_cls:
        mock_settings_cls.return_value.get.return_value = "test-cookie"
        mock_dl_cls.return_value.download_column.return_value = {
            "title": "测试标题",
            "sections": [],
            "full_text": "下载的内容"
        }
        with app.app_context():
            novel = service.download_from_url(
                "https://www.zhihu.com/market/paid_column/1/section/2",
                name="自定义名称"
            )
            assert novel.name == "自定义名称"
            assert novel.original_text == "下载的内容"
            assert novel.share_url == "https://www.zhihu.com/market/paid_column/1/section/2"
            assert novel.word_count > 0


def test_download_from_url_uses_title_when_no_name(service, app):
    """download_from_url 不传 name 时使用专栏标题"""
    with patch('cinegacha.services.novel_service.ZhihuDownloader') as mock_dl_cls, \
         patch('cinegacha.services.novel_service.SettingsService') as mock_settings_cls:
        mock_settings_cls.return_value.get.return_value = "test-cookie"
        mock_dl_cls.return_value.download_column.return_value = {
            "title": "专栏标题",
            "sections": [],
            "full_text": "内容"
        }
        with app.app_context():
            novel = service.download_from_url(
                "https://www.zhihu.com/market/paid_column/1/section/2"
            )
            assert novel.name == "专栏标题"


def test_download_from_url_no_cookie_raises(service, app):
    """download_from_url 无 cookie 抛 ZhihuAuthError"""
    with patch('cinegacha.services.novel_service.SettingsService') as mock_cls:
        mock_cls.return_value.get.return_value = None
        from cinegacha.services.zhihu_downloader import ZhihuAuthError
        with app.app_context():
            with pytest.raises(ZhihuAuthError):
                service.download_from_url(
                    "https://www.zhihu.com/market/paid_column/1/section/2"
                )


def test_download_from_url_clean_failure_not_fatal(service, app):
    """download_from_url 清洗失败不影响下载"""
    with patch('cinegacha.services.novel_service.ZhihuDownloader') as mock_dl_cls, \
         patch('cinegacha.services.novel_service.SettingsService') as mock_settings_cls, \
         patch.object(NovelService, 'clean_text', side_effect=Exception("clean error")):
        mock_settings_cls.return_value.get.return_value = "test-cookie"
        mock_dl_cls.return_value.download_column.return_value = {
            "title": "标题",
            "sections": [],
            "full_text": "内容"
        }
        with app.app_context():
            novel = service.download_from_url(
                "https://www.zhihu.com/market/paid_column/1/section/2"
            )
            assert novel.name == "标题"
            assert novel.original_text == "内容"
