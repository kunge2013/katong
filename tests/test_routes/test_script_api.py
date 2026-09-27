# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import pytest
import json
from cinegacha import db
from cinegacha.models.novel import Novel
from cinegacha.models.project import Project


@pytest.fixture
def client(app):
    """测试客户端"""
    return app.test_client()


@pytest.fixture
def sample_project(app):
    """创建测试项目"""
    with app.app_context():
        novel = Novel(name="测试小说", content="测试内容" * 100)
        db.session.add(novel)
        db.session.flush()

        project = Project(name="测试项目", novel_id=novel.id)
        db.session.add(project)
        db.session.commit()

        return project.id


def test_list_scripts(client, sample_project, app):
    """GET /api/projects/<id>/scripts - 列表分镜"""
    with app.app_context():
        # 创建测试分镜
        from cinegacha.models.script import Script
        script1 = Script(project_id=sample_project, shot_id=1, shot_index=1, content="镜头1")
        script2 = Script(project_id=sample_project, shot_id=2, shot_index=2, content="镜头2")
        db.session.add_all([script1, script2])
        db.session.commit()

        response = client.get(f'/api/projects/{sample_project}/scripts')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 2


def test_get_script(client, sample_project, app):
    """GET /api/scripts/<id> - 获取详情"""
    with app.app_context():
        from cinegacha.models.script import Script
        script = Script(project_id=sample_project, shot_id=1, shot_index=1, content="镜头描述")
        db.session.add(script)
        db.session.commit()

        response = client.get(f'/api/scripts/{script.id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['content'] == "镜头描述"


def test_get_nonexistent_script(client):
    """GET /api/scripts/<id> - 分镜不存在"""
    response = client.get('/api/scripts/99999')

    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] is False


def test_update_script(client, sample_project, app):
    """PUT /api/scripts/<id> - 更新分镜"""
    with app.app_context():
        from cinegacha.models.script import Script
        script = Script(project_id=sample_project, shot_id=1, shot_index=1, content="原始内容")
        db.session.add(script)
        db.session.commit()

        response = client.put(f'/api/scripts/{script.id}', json={
            "content": "更新内容"
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


def test_delete_script(client, sample_project, app):
    """DELETE /api/scripts/<id> - 删除分镜"""
    with app.app_context():
        from cinegacha.models.script import Script
        script = Script(project_id=sample_project, shot_id=1, shot_index=1, content="镜头1")
        db.session.add(script)
        db.session.commit()

        response = client.delete(f'/api/scripts/{script.id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


def test_derive_image_prompt_missing_api_key(client, sample_project, app):
    """POST /api/scripts/<id>/derive - 缺少 API key"""
    with app.app_context():
        from cinegacha.models.script import Script
        script = Script(project_id=sample_project, shot_id=1, shot_index=1, content="镜头")
        db.session.add(script)
        db.session.commit()

        response = client.post(f'/api/scripts/{script.id}/derive', json={})

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'MISSING_API_KEY' in data['error']['code']
