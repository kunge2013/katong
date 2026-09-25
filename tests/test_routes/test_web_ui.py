# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import pytest
from cinegacha import db
from cinegacha.models.novel import Novel


@pytest.fixture
def client(app):
    """测试客户端"""
    return app.test_client()


def test_index_page(client):
    """测试首页"""
    response = client.get('/')
    assert response.status_code == 200
    assert '雪漫画' in response.data.decode('utf-8')
    assert 'CineGacha' in response.data.decode('utf-8')


def test_novels_list_page(client, app):
    """测试小说列表页面"""
    with app.app_context():
        # 创建测试小说
        novel = Novel(name="测试小说", content="测试内容")
        db.session.add(novel)
        db.session.commit()

        response = client.get('/novels')
        assert response.status_code == 200
        assert '小说列表' in response.data.decode('utf-8')
        assert '测试小说' in response.data.decode('utf-8')


def test_novel_new_page(client):
    """测试创建小说页面"""
    response = client.get('/novels/new')
    assert response.status_code == 200
    assert '创建新小说' in response.data.decode('utf-8')
    assert '小说名称' in response.data.decode('utf-8')


def test_novel_detail_page(client, app):
    """测试小说详情页面"""
    with app.app_context():
        novel = Novel(name="测试小说", content="测试内容", word_count=100)
        db.session.add(novel)
        db.session.commit()

        response = client.get(f'/novels/{novel.id}')
        assert response.status_code == 200
        assert '测试小说' in response.data.decode('utf-8')
        assert '清洗状态' in response.data.decode('utf-8')


def test_novel_detail_not_found(client):
    """测试小说详情 - 小说不存在"""
    response = client.get('/novels/99999')
    # 应该重定向到列表页
    assert response.status_code == 302


def test_error_handler_404(client):
    """测试 404 错误处理器"""
    response = client.get('/nonexistent-page-that-does-not-exist')
    assert response.status_code == 404


def test_index_shows_counts(client, app):
    """测试首页显示统计数据"""
    with app.app_context():
        # 创建测试数据
        novel = Novel(name="小说1", content="内容1")
        db.session.add(novel)
        db.session.commit()

        response = client.get('/')
        assert response.status_code == 200
        # 检查是否包含统计信息
        data = response.data.decode('utf-8')
        assert '小说数量' in data or 'novel-count' in data


# [AGC:START] tool=Cc author=fangkun
def test_settings_page(client):
    """测试设置页面"""
    response = client.get('/settings')
    assert response.status_code == 200
    assert '设置' in response.data.decode('utf-8')


# [AGC:END]
