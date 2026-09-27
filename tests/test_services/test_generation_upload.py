# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import pytest
from unittest.mock import Mock, patch
from cinegacha import db
from cinegacha.services.generation_service import GenerationService
from cinegacha.services.upload_service import UploadService
from cinegacha.models.novel import Novel
from cinegacha.models.project import Project
from cinegacha.models.script import Script
from cinegacha.models.role import Role
from cinegacha.models.role import RoleTag


@pytest.fixture
def generation_service():
    """生成服务实例"""
    return GenerationService()


@pytest.fixture
def upload_service():
    """上传服务实例"""
    return UploadService()


@pytest.fixture
def sample_project_with_scripts(app):
    """创建带分镜的测试项目"""
    with app.app_context():
        novel = Novel(name="测试小说", content="测试内容")
        db.session.add(novel)
        db.session.flush()

        project = Project(name="测试项目", novel_id=novel.id)
        db.session.add(project)
        db.session.flush()

        # 创建分镜
        script1 = Script(
            project_id=project.id,
            shot_id=1,
            shot_index=1,
            content="镜头1",
            image_prompt="图像提示词1"
        )
        script2 = Script(
            project_id=project.id,
            shot_id=2,
            shot_index=2,
            content="镜头2",
            image_prompt="图像提示词2"
        )
        db.session.add_all([script1, script2])
        db.session.commit()

        return {
            "novel_id": novel.id,
            "project_id": project.id,
            "script_ids": [script1.id, script2.id]
        }


def test_generate_image(generation_service, sample_project_with_scripts, app):
    """测试单张图像生成"""
    with app.app_context():
        script_id = sample_project_with_scripts["script_ids"][0]
        project_id = sample_project_with_scripts["project_id"]

        local_path = generation_service.generate_image(
            script_id=script_id,
            image_prompt="测试提示词",
            project_id=project_id
        )

        assert local_path is not None
        assert "Output" in local_path
        assert str(project_id) in local_path
        assert f"shot_{script_id}" in local_path


def test_generate_all(generation_service, sample_project_with_scripts, app):
    """测试批量图像生成"""
    with app.app_context():
        project_id = sample_project_with_scripts["project_id"]

        results = generation_service.generate_all(project_id)

        assert len(results) == 2
        assert all(r["status"] == "success" for r in results)


def test_sign_url(upload_service):
    """测试签名 URL 生成"""
    object_key = "test_object.jpeg"
    signed_url = upload_service._sign_url(object_key)

    assert "cloudflarestorage.com" in signed_url
    assert object_key in signed_url
    assert "X-Amz-Algorithm=AWS4-HMAC-SHA256" in signed_url
    assert "X-Amz-Expires=259200" in signed_url  # 72h


def test_upload_to_cloud(upload_service, app):
    """测试上传到云端"""
    with app.app_context():
        # 创建测试资产
        novel = Novel(name="测试小说", content="内容")
        db.session.add(novel)
        db.session.flush()

        project = Project(name="测试项目", novel_id=novel.id)
        db.session.add(project)
        db.session.flush()

        role = Role(name="测试角色", novel_id=novel.id, project_id=project.id, content="描述")
        db.session.add(role)
        db.session.flush()

        tag = RoleTag(role_id=role.id, tag_category="类型", tag_value="角色")
        db.session.add(tag)
        db.session.commit()

        # 测试上传
        signed_url = upload_service.upload_to_cloud("/fake/path.png", role.id)

        assert signed_url is not None
        assert "cloudflarestorage.com" in signed_url

        # 验证数据库更新
        updated_role = db.session.get(Role, role.id)
        assert updated_role.role_url is not None
