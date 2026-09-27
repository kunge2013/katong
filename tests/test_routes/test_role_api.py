# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import pytest
from cinegacha import db
from cinegacha.models.novel import Novel
from cinegacha.models.project import Project


@pytest.fixture
def client(app):
    """测试客户端"""
    return app.test_client()


@pytest.fixture
def novel_and_project(app):
    """创建测试小说和项目"""
    with app.app_context():
        novel = Novel(name="测试小说", content="测试内容")
        db.session.add(novel)
        db.session.flush()

        project = Project(name="测试项目", novel_id=novel.id)
        db.session.add(project)
        db.session.commit()

        return {"novel_id": novel.id, "project_id": project.id}


def test_create_asset_api(client, novel_and_project):
    """POST /api/projects/<id>/assets - 创建资产"""
    project_id = novel_and_project["project_id"]
    novel_id = novel_and_project["novel_id"]

    response = client.post(f'/api/projects/{project_id}/assets', json={
        "name": "明溪",
        "novel_id": novel_id,
        "type": "角色",
        "content": "12岁女孩，活泼可爱"
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['name'] == "明溪"
    assert data['data']['type'] == "角色"
    assert data['data']['id'] is not None


def test_create_asset_missing_name(client, novel_and_project):
    """POST /api/projects/<id>/assets - 缺少名称"""
    project_id = novel_and_project["project_id"]
    novel_id = novel_and_project["novel_id"]

    response = client.post(f'/api/projects/{project_id}/assets', json={
        "novel_id": novel_id,
        "type": "角色",
        "content": "描述"
    })

    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'MISSING_NAME' in data['error']['code']


def test_create_asset_missing_novel_id(client, novel_and_project):
    """POST /api/projects/<id>/assets - 缺少小说 ID"""
    project_id = novel_and_project["project_id"]

    response = client.post(f'/api/projects/{project_id}/assets', json={
        "name": "明溪",
        "type": "角色",
        "content": "描述"
    })

    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'MISSING_NOVEL_ID' in data['error']['code']


def test_create_asset_missing_type(client, novel_and_project):
    """POST /api/projects/<id>/assets - 缺少类型"""
    project_id = novel_and_project["project_id"]
    novel_id = novel_and_project["novel_id"]

    response = client.post(f'/api/projects/{project_id}/assets', json={
        "name": "明溪",
        "novel_id": novel_id,
        "content": "描述"
    })

    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'MISSING_TYPE' in data['error']['code']


def test_list_assets_api(client, novel_and_project):
    """GET /api/projects/<id>/assets - 列表资产"""
    project_id = novel_and_project["project_id"]
    novel_id = novel_and_project["novel_id"]

    # 创建多个资产
    for i in range(3):
        client.post(f'/api/projects/{project_id}/assets', json={
            "name": f"资产{i}",
            "novel_id": novel_id,
            "type": "角色",
            "content": f"描述{i}"
        })

    response = client.get(f'/api/projects/{project_id}/assets')

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data['data']) == 3
    assert data['total'] == 3


def test_list_assets_by_type_api(client, novel_and_project):
    """GET /api/projects/<id>/assets?type=角色 - 按类型过滤"""
    project_id = novel_and_project["project_id"]
    novel_id = novel_and_project["novel_id"]

    # 创建不同类型的资产
    client.post(f'/api/projects/{project_id}/assets', json={
        "name": "角色1", "novel_id": novel_id, "type": "角色", "content": "描述"
    })
    client.post(f'/api/projects/{project_id}/assets', json={
        "name": "角色2", "novel_id": novel_id, "type": "角色", "content": "描述"
    })
    client.post(f'/api/projects/{project_id}/assets', json={
        "name": "场景1", "novel_id": novel_id, "type": "场景", "content": "描述"
    })

    # 只获取角色
    response = client.get(f'/api/projects/{project_id}/assets?type=角色')

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data['data']) == 2


def test_get_asset_api(client, novel_and_project):
    """GET /api/assets/<id> - 获取详情"""
    project_id = novel_and_project["project_id"]
    novel_id = novel_and_project["novel_id"]

    # 创建资产
    create_resp = client.post(f'/api/projects/{project_id}/assets', json={
        "name": "明溪",
        "novel_id": novel_id,
        "type": "角色",
        "content": "12岁女孩"
    })
    asset_id = create_resp.get_json()['data']['id']

    # 获取详情
    response = client.get(f'/api/assets/{asset_id}')

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['name'] == "明溪"
    assert data['data']['type'] == "角色"


def test_get_nonexistent_asset(client):
    """GET /api/assets/<id> - 资产不存在"""
    response = client.get('/api/assets/99999')

    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] is False
    assert 'ASSET_NOT_FOUND' in data['error']['code']


def test_update_asset_api(client, novel_and_project):
    """PUT /api/assets/<id> - 更新资产"""
    project_id = novel_and_project["project_id"]
    novel_id = novel_and_project["novel_id"]

    # 创建
    create_resp = client.post(f'/api/projects/{project_id}/assets', json={
        "name": "原始名称",
        "novel_id": novel_id,
        "type": "角色",
        "content": "描述"
    })
    asset_id = create_resp.get_json()['data']['id']

    # 更新
    response = client.put(f'/api/assets/{asset_id}', json={"name": "更新后名称"})

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['name'] == "更新后名称"


def test_delete_asset_api(client, novel_and_project):
    """DELETE /api/assets/<id> - 删除资产"""
    project_id = novel_and_project["project_id"]
    novel_id = novel_and_project["novel_id"]

    # 创建
    create_resp = client.post(f'/api/projects/{project_id}/assets', json={
        "name": "测试",
        "novel_id": novel_id,
        "type": "角色",
        "content": "描述"
    })
    asset_id = create_resp.get_json()['data']['id']

    # 删除
    response = client.delete(f'/api/assets/{asset_id}')

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

    # 验证已删除
    get_resp = client.get(f'/api/assets/{asset_id}')
    assert get_resp.status_code == 404
