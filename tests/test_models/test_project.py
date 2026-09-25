# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from cinegacha import db
from cinegacha.models.novel import Novel
from cinegacha.models.project import Project


def test_create_project(client):
    """创建项目"""
    novel = Novel(name="测试小说", original_text="内容")
    db.session.add(novel)
    db.session.commit()

    project = Project(
        name="漫画项目",
        novel_id=novel.id,
        mode="manga"
    )
    db.session.add(project)
    db.session.commit()

    assert project.id is not None
    assert project.novel_id == novel.id
    assert project.mode == "manga"


def test_project_with_art_style(client):
    """项目画风配置"""
    novel = Novel(name="测试", original_text="内容")
    db.session.add(novel)
    db.session.commit()

    project = Project(
        name="测试项目",
        novel_id=novel.id,
        img_prompt_prefix="韩系漫画风格",
        img_prompt_suffix="高质量渲染"
    )
    db.session.add(project)
    db.session.commit()

    assert "韩系" in project.img_prompt_prefix
