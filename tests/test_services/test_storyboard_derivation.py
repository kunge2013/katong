# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import pytest
from unittest.mock import Mock, patch
from cinegacha import db
from cinegacha.services.storyboard_service import StoryboardService
from cinegacha.services.derivation_service import DerivationService
from cinegacha.models.novel import Novel
from cinegacha.models.project import Project
from cinegacha.models.script import Script
from cinegacha.models.role import Role, RoleTag
import json


@pytest.fixture
def storyboard_service():
    """分镜服务实例"""
    return StoryboardService()


@pytest.fixture
def derivation_service():
    """推导服务实例"""
    return DerivationService()


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


def test_chunk_text(storyboard_service):
    """测试文本分块"""
    text = "a" * 2000
    chunks = storyboard_service._chunk_text(text, 900)
    assert len(chunks) == 3
    assert len(chunks[0]) == 900
    assert len(chunks[1]) == 900
    assert len(chunks[2]) == 200


@patch('cinegacha.services.storyboard_service.LLMClient')
def test_split_storyboard(mock_llm_client_class, storyboard_service, sample_project, app):
    """测试分镜拆分"""
    with app.app_context():
        # Mock LLM 响应
        mock_llm = Mock()
        mock_llm_client_class.return_value = mock_llm
        mock_llm.call_deepseek.return_value = '''
[
  {"content": "镜头1描述", "presets": ["角色1"]},
  {"content": "镜头2描述", "presets": ["角色1", "场景1"]}
]
'''
        mock_llm._parse_json_response.return_value = [
            {"content": "镜头1描述", "presets": ["角色1"]},
            {"content": "镜头2描述", "presets": ["角色1", "场景1"]}
        ]

        scripts = storyboard_service.split_storyboard(sample_project, "fake_api_key")

        assert len(scripts) > 0
        assert scripts[0].project_id == sample_project
        assert scripts[0].shot_index == 1


def test_get_scripts(storyboard_service, sample_project, app):
    """测试获取分镜列表"""
    with app.app_context():
        # 创建测试分镜
        script1 = Script(project_id=sample_project, shot_id=1, shot_index=1, content="镜头1")
        script2 = Script(project_id=sample_project, shot_id=2, shot_index=2, content="镜头2")
        db.session.add_all([script1, script2])
        db.session.commit()

        scripts = storyboard_service.get_scripts(sample_project)
        assert len(scripts) == 2
        assert scripts[0].shot_index == 1
        assert scripts[1].shot_index == 2


def test_update_script(storyboard_service, sample_project, app):
    """测试更新分镜"""
    with app.app_context():
        script = Script(project_id=sample_project, shot_id=1, shot_index=1, content="原始内容")
        db.session.add(script)
        db.session.commit()

        updated = storyboard_service.update_script(script.id, content="更新内容")
        assert updated.content == "更新内容"


def test_delete_script(storyboard_service, sample_project, app):
    """测试删除分镜"""
    with app.app_context():
        script = Script(project_id=sample_project, shot_id=1, shot_index=1, content="镜头1")
        db.session.add(script)
        db.session.commit()

        result = storyboard_service.delete_script(script.id)
        assert result is True

        deleted = db.session.get(Script, script.id)
        assert deleted is None


def test_match_assets(derivation_service, sample_project, app):
    """测试资产匹配"""
    with app.app_context():
        # 创建测试资产
        novel = db.session.get(Project, sample_project).novel_id

        # 创建角色
        role1 = Role(name="明溪", novel_id=novel, project_id=sample_project, content="12岁女孩")
        db.session.add(role1)
        db.session.flush()
        tag1 = RoleTag(role_id=role1.id, tag_category="类型", tag_value="角色")
        db.session.add(tag1)

        # 创建场景
        role2 = Role(name="明家祠堂", novel_id=novel, project_id=sample_project, content="古色古香")
        db.session.add(role2)
        db.session.flush()
        tag2 = RoleTag(role_id=role2.id, tag_category="类型", tag_value="场景")
        db.session.add(tag2)

        db.session.commit()

        # 测试匹配
        presets = ["明溪", "明家祠堂"]
        context = derivation_service._match_assets(presets, sample_project)

        assert len(context["characters"]) == 1
        assert context["characters"][0]["name"] == "明溪"
        assert len(context["scenes"]) == 1
        assert context["scenes"][0]["name"] == "明家祠堂"


def test_assemble_prompt(derivation_service):
    """测试提示词组装"""
    asset_context = {
        "characters": [{"name": "明溪", "description": "12岁女孩"}],
        "scenes": [{"name": "明家祠堂", "description": "古色古香"}],
        "props": []
    }

    prompt = derivation_service._assemble_prompt(
        story_content="明溪站在祠堂门口",
        asset_context=asset_context,
        img_prompt_prefix="请生成图像",
        img_prompt_suffix="注意细节"
    )

    assert "明溪" in prompt
    assert "明家祠堂" in prompt
    assert "12岁女孩" in prompt
    assert "古色古香" in prompt


@patch('cinegacha.services.derivation_service.LLMClient')
def test_derive_image_prompt(mock_llm_client_class, derivation_service, sample_project, app):
    """测试图像提示词推导"""
    with app.app_context():
        # 创建测试分镜
        script = Script(
            project_id=sample_project,
            shot_id=1,
            shot_index=1,
            content="明溪站在祠堂门口",
            presets=json.dumps(["明溪", "明家祠堂"], ensure_ascii=False)
        )
        db.session.add(script)
        db.session.commit()

        # Mock LLM 响应
        mock_llm = Mock()
        mock_llm_client_class.return_value = mock_llm
        mock_llm.call_deepseek.return_value = "生成的图像提示词，包含画面描述和版式说明"

        result = derivation_service.derive_image_prompt(script.id, "fake_api_key")

        assert result.image_prompt is not None
        assert len(result.image_prompt) > 0
