# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from cinegacha import db
from cinegacha.models.novel import Novel
from cinegacha.models.role import Role, RoleTag


def test_create_character(client):
    """创建角色"""
    novel = Novel(name="测试小说", original_text="内容")
    db.session.add(novel)
    db.session.commit()

    role = Role(
        name="明溪",
        novel_id=novel.id,
        content="12岁古代汉族小女孩，肤色小麦色，圆脸蛋带着婴儿肥..."
    )
    # 通过 RoleTag 区分资产类型
    tag = RoleTag(role=role, tag_category="类型", tag_value="角色")
    db.session.add_all([role, tag])
    db.session.commit()

    assert role.id is not None
    assert role.name == "明溪"
    assert role.content is not None
    assert len(role.content) > 10


def test_create_scene(client):
    """创建场景"""
    novel = Novel(name="测试", original_text="内容")
    db.session.add(novel)
    db.session.commit()

    role = Role(
        name="明家祠堂夜晚",
        novel_id=novel.id,
        content="古色古香的祠堂，月光透过窗棂洒下..."
    )
    tag = RoleTag(role=role, tag_category="类型", tag_value="场景")
    db.session.add_all([role, tag])
    db.session.commit()

    assert role.name.endswith("夜晚")


def test_role_with_tags(client):
    """角色标签"""
    novel = Novel(name="测试", original_text="内容")
    db.session.add(novel)
    db.session.commit()

    role = Role(name="明溪", novel_id=novel.id, content="12岁女孩...")
    db.session.add(role)
    db.session.commit()

    tag1 = RoleTag(role_id=role.id, tag_category="性别", tag_value="女")
    tag2 = RoleTag(role_id=role.id, tag_category="时代", tag_value="古代")
    db.session.add_all([tag1, tag2])
    db.session.commit()

    assert len(role.tags) == 2
    assert any(t.tag_value == "女" for t in role.tags)


def test_role_dual_description(client):
    """双层描述"""
    novel = Novel(name="测试", original_text="内容")
    db.session.add(novel)
    db.session.commit()

    role = Role(
        name="明溪",
        novel_id=novel.id,
        content="12岁古代小女孩...",  # 中文基础描述
        content_word2="strictly isolated on pure white background..."  # 英文增强
    )
    db.session.add(role)
    db.session.commit()

    assert role.content.startswith("12岁")
    assert "white background" in role.content_word2
