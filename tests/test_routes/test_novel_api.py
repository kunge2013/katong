# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import pytest
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
