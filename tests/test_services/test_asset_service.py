# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import pytest
from cinegacha import db
from cinegacha.services.asset_service import AssetService
from cinegacha.models.role import Role, RoleTag


@pytest.fixture
def asset_service():
    """资产服务实例"""
    return AssetService()


@pytest.fixture
def sample_character(app, asset_service):
    """创建测试角色"""
    with app.app_context():
        from cinegacha.models.novel import Novel
        from cinegacha.models.project import Project

        # 创建小说和项目
        novel = Novel(name="测试小说", content="测试内容")
        db.session.add(novel)
        db.session.flush()

        project = Project(name="测试项目", novel_id=novel.id)
        db.session.add(project)
        db.session.commit()

        # 创建角色
        asset = asset_service.create_asset(
            name="主角",
            novel_id=novel.id,
            project_id=project.id,
            role_type="角色",
            content="主角描述"
        )

        return asset.id  # 返回 ID 而不是对象，避免 detached instance


def test_create_character(asset_service, app):
    """创建角色资产"""
    with app.app_context():
        from cinegacha.models.novel import Novel
        from cinegacha.models.project import Project

        novel = Novel(name="测试小说", content="测试内容")
        db.session.add(novel)
        db.session.flush()

        project = Project(name="测试项目", novel_id=novel.id)
        db.session.add(project)
        db.session.commit()

        # 创建角色
        asset = asset_service.create_asset(
            name="明溪",
            novel_id=novel.id,
            project_id=project.id,
            role_type="角色",
            content="12岁女孩，活泼可爱"
        )

        assert asset.id is not None
        assert asset.name == "明溪"
        assert asset.novel_id == novel.id
        assert asset.project_id == project.id
        assert asset.content == "12岁女孩，活泼可爱"

        # 验证标签
        tags = db.session.query(RoleTag).filter(RoleTag.role_id == asset.id).all()
        assert len(tags) == 1
        assert tags[0].tag_category == "类型"
        assert tags[0].tag_value == "角色"


def test_create_scene(asset_service, app):
    """创建场景资产"""
    with app.app_context():
        from cinegacha.models.novel import Novel
        from cinegacha.models.project import Project

        novel = Novel(name="测试小说", content="测试内容")
        db.session.add(novel)
        db.session.flush()

        project = Project(name="测试项目", novel_id=novel.id)
        db.session.add(project)
        db.session.commit()

        # 创建场景
        asset = asset_service.create_asset(
            name="明家祠堂夜晚",
            novel_id=novel.id,
            project_id=project.id,
            role_type="场景",
            content="古色古香的祠堂，月光透过窗棂"
        )

        assert asset.id is not None
        assert asset.name == "明家祠堂夜晚"

        # 验证标签
        tags = db.session.query(RoleTag).filter(RoleTag.role_id == asset.id).all()
        assert len(tags) == 1
        assert tags[0].tag_value == "场景"


def test_create_prop(asset_service, app):
    """创建道具资产"""
    with app.app_context():
        from cinegacha.models.novel import Novel
        from cinegacha.models.project import Project

        novel = Novel(name="测试小说", content="测试内容")
        db.session.add(novel)
        db.session.flush()

        project = Project(name="测试项目", novel_id=novel.id)
        db.session.add(project)
        db.session.commit()

        # 创建道具
        asset = asset_service.create_asset(
            name="婚书",
            novel_id=novel.id,
            project_id=project.id,
            role_type="道具",
            content="古老的婚书，泛黄的纸张"
        )

        assert asset.id is not None
        assert asset.name == "婚书"

        # 验证标签
        tags = db.session.query(RoleTag).filter(RoleTag.role_id == asset.id).all()
        assert len(tags) == 1
        assert tags[0].tag_value == "道具"


def test_get_asset(asset_service, sample_character, app):
    """获取资产"""
    with app.app_context():
        asset = asset_service.get_asset(sample_character)
        assert asset is not None
        assert asset.name == "主角"


def test_list_assets_all(asset_service, app):
    """列出所有资产"""
    with app.app_context():
        from cinegacha.models.novel import Novel
        from cinegacha.models.project import Project

        novel = Novel(name="测试小说", content="测试内容")
        db.session.add(novel)
        db.session.flush()

        project = Project(name="测试项目", novel_id=novel.id)
        db.session.add(project)
        db.session.commit()

        # 创建多个资产
        asset_service.create_asset(name="角色1", novel_id=novel.id, project_id=project.id, role_type="角色", content="描述1")
        asset_service.create_asset(name="场景1", novel_id=novel.id, project_id=project.id, role_type="场景", content="描述2")
        asset_service.create_asset(name="道具1", novel_id=novel.id, project_id=project.id, role_type="道具", content="描述3")

        assets = asset_service.list_assets(project_id=project.id)
        assert len(assets) == 3


def test_list_assets_by_type(asset_service, app):
    """按类型列出资产"""
    with app.app_context():
        from cinegacha.models.novel import Novel
        from cinegacha.models.project import Project

        novel = Novel(name="测试小说", content="测试内容")
        db.session.add(novel)
        db.session.flush()

        project = Project(name="测试项目", novel_id=novel.id)
        db.session.add(project)
        db.session.commit()

        # 创建多个资产
        asset_service.create_asset(name="角色1", novel_id=novel.id, project_id=project.id, role_type="角色", content="描述1")
        asset_service.create_asset(name="角色2", novel_id=novel.id, project_id=project.id, role_type="角色", content="描述2")
        asset_service.create_asset(name="场景1", novel_id=novel.id, project_id=project.id, role_type="场景", content="描述3")

        # 只列出角色
        characters = asset_service.list_assets(project_id=project.id, role_type="角色")
        assert len(characters) == 2

        # 只列出场景
        scenes = asset_service.list_assets(project_id=project.id, role_type="场景")
        assert len(scenes) == 1


def test_update_asset(asset_service, sample_character, app):
    """更新资产"""
    with app.app_context():
        updated = asset_service.update_asset(sample_character, name="更新后的主角")
        assert updated.name == "更新后的主角"


def test_delete_asset(asset_service, sample_character, app):
    """删除资产"""
    with app.app_context():
        result = asset_service.delete_asset(sample_character)
        assert result is True

        # 验证已删除
        asset = asset_service.get_asset(sample_character)
        assert asset is None

        # 验证标签也被删除
        tags = db.session.query(RoleTag).filter(RoleTag.role_id == sample_character).all()
        assert len(tags) == 0
