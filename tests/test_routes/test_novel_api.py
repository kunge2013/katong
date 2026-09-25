# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import pytest
from unittest.mock import patch
from cinegacha import db
from cinegacha.models.novel import Novel


@pytest.fixture
def client(app):
    """测试客户端"""
    return app.test_client()


def test_create_novel_api(client):
    """POST /api/novels - 创建小说"""
    response = client.post('/api/novels', json={
        "name": "测试小说",
        "text": "这是小说内容"
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['name'] == "测试小说"
    assert data['data']['id'] is not None


def test_create_novel_missing_name(client):
    """POST /api/novels - 缺少名称"""
    response = client.post('/api/novels', json={
        "text": "内容"
    })

    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'MISSING_NAME' in data['error']['code']


def test_list_novels_api(client):
    """GET /api/novels - 列表小说"""
    # 先创建几个小说
    for i in range(3):
        client.post('/api/novels', json={"name": f"小说{i}", "text": f"内容{i}"})

    response = client.get('/api/novels?page=1&per_page=10')

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data['data']) == 3
    assert data['total'] == 3


def test_get_novel_api(client):
    """GET /api/novels/<id> - 获取详情"""
    # 创建小说
    create_resp = client.post('/api/novels', json={"name": "测试", "text": "内容"})
    novel_id = create_resp.get_json()['data']['id']

    # 获取详情
    response = client.get(f'/api/novels/{novel_id}')

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['name'] == "测试"


def test_get_nonexistent_novel(client):
    """GET /api/novels/<id> - 小说不存在"""
    response = client.get('/api/novels/99999')

    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] is False
    assert 'NOVEL_NOT_FOUND' in data['error']['code']


def test_clean_novel_api(client):
    """POST /api/novels/<id>/clean - 清洗小说"""
    # 创建小说
    create_resp = client.post('/api/novels', json={
        "name": "测试",
        "text": "小说内容 [连载]\r\nHello, world!"
    })
    novel_id = create_resp.get_json()['data']['id']

    # 清洗
    response = client.post(f'/api/novels/{novel_id}/clean')

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['is_format_cleaned'] == 1
    assert data['data']['is_serial_cleaned'] == 1
    assert data['data']['is_punct_cleaned'] == 1


def test_clean_nonexistent_novel(client):
    """POST /api/novels/<id>/clean - 小说不存在"""
    response = client.post('/api/novels/99999/clean')

    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] is False


def test_update_novel_api(client):
    """PUT /api/novels/<id> - 更新小说"""
    # 创建
    create_resp = client.post('/api/novels', json={"name": "原始", "text": "内容"})
    novel_id = create_resp.get_json()['data']['id']

    # 更新
    response = client.put(f'/api/novels/{novel_id}', json={"name": "更新后"})

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['name'] == "更新后"


def test_delete_novel_api(client):
    """DELETE /api/novels/<id> - 删除小说"""
    # 创建
    create_resp = client.post('/api/novels', json={"name": "测试", "text": "内容"})
    novel_id = create_resp.get_json()['data']['id']

    # 删除
    response = client.delete(f'/api/novels/{novel_id}')

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

    # 验证已删除
    get_resp = client.get(f'/api/novels/{novel_id}')
    assert get_resp.status_code == 404


# ── Download endpoint tests ──────────────────────────────────────────


# [AGC:START] tool=Cc author=fangkun
def test_download_novel_success(client):
    """POST /api/novels/download - 下载成功"""
    with patch('cinegacha.services.novel_service.ZhihuDownloader') as mock_dl_cls, \
         patch('cinegacha.services.novel_service.SettingsService') as mock_settings_cls:
        mock_settings = mock_settings_cls.return_value
        mock_settings.get.return_value = "test-cookie"
        mock_dl = mock_dl_cls.return_value
        mock_dl.download_column.return_value = {
            "title": "测试小说",
            "sections": [{"id": 1, "title": "第一章", "text": "内容"}],
            "full_text": "测试内容"
        }
        response = client.post(
            '/api/novels/download',
            json={"url": "https://www.zhihu.com/market/paid_column/123/section/456"}
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['name'] == '测试小说'
        assert data['data']['word_count'] == 4  # len("测试内容")
# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_download_novel_missing_url(client):
    """POST /api/novels/download - 缺少 URL"""
    response = client.post('/api/novels/download', json={})
    assert response.status_code == 400
# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_download_novel_invalid_url(client):
    """POST /api/novels/download - 无效 URL 格式"""
    response = client.post('/api/novels/download',
                          json={"url": "https://example.com/foo"})
    assert response.status_code == 400
    data = response.get_json()
    assert data['error']['code'] == 'INVALID_URL'
# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_download_novel_no_cookie(client):
    """POST /api/novels/download - 未登录知乎"""
    with patch('cinegacha.services.novel_service.SettingsService') as mock_cls:
        mock_settings = mock_cls.return_value
        mock_settings.get.return_value = None
        response = client.post(
            '/api/novels/download',
            json={"url": "https://www.zhihu.com/market/paid_column/123/section/456"}
        )
        assert response.status_code == 401
        data = response.get_json()
        assert data['error']['code'] == 'AUTH_REQUIRED'
# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_download_novel_scrape_error(client):
    """POST /api/novels/download - 抓取失败"""
    from cinegacha.services.zhihu_downloader import ZhihuScrapeError
    with patch('cinegacha.services.novel_service.ZhihuDownloader') as mock_dl_cls, \
         patch('cinegacha.services.novel_service.SettingsService') as mock_settings_cls:
        mock_settings_cls.return_value.get.return_value = "test-cookie"
        mock_dl_cls.return_value.download_column.side_effect = ZhihuScrapeError("network error")
        response = client.post(
            '/api/novels/download',
            json={"url": "https://www.zhihu.com/market/paid_column/123/section/456"}
        )
        assert response.status_code == 502
# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_create_novel_with_zhihu_url_auto_downloads(client):
    """POST /api/novels - 传入知乎 URL 时自动下载"""
    with patch('cinegacha.services.novel_service.ZhihuDownloader') as mock_dl_cls, \
         patch('cinegacha.services.novel_service.SettingsService') as mock_settings_cls:
        mock_settings_cls.return_value.get.return_value = "test-cookie"
        mock_dl_cls.return_value.download_column.return_value = {
            "title": "Auto",
            "sections": [],
            "full_text": "自动下载的内容"
        }
        response = client.post(
            '/api/novels',
            json={"name": "Test", "url": "https://www.zhihu.com/market/paid_column/1/section/2"}
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['name'] == 'Auto'
# [AGC:END]
