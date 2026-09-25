# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import json
from cinegacha import db
from cinegacha.models.novel import Novel
from cinegacha.models.project import Project
from cinegacha.models.script import Script, ScriptCamera


def test_create_script(client):
    """创建分镜"""
    novel = Novel(name="测试", original_text="内容")
    db.session.add(novel)
    db.session.commit()

    project = Project(name="项目", novel_id=novel.id)
    db.session.add(project)
    db.session.commit()

    script = Script(
        project_id=project.id,
        shot_index=1,
        content="明溪走进祠堂",
        presets=json.dumps(["明溪", "明家祠堂夜晚"], ensure_ascii=False)
    )
    db.session.add(script)
    db.session.commit()

    assert script.id is not None
    assert script.shot_index == 1
    presets = json.loads(script.presets)
    assert "明溪" in presets


def test_script_with_image_prompt(client):
    """分镜图像提示词"""
    novel = Novel(name="测试", original_text="内容")
    db.session.add(novel)
    db.session.commit()

    project = Project(name="项目", novel_id=novel.id)
    db.session.add(project)
    db.session.commit()

    script = Script(
        project_id=project.id,
        shot_index=1,
        content="场景描述",
        image_prompt="韩系漫画风格，明溪站在祠堂前，月光洒下..."
    )
    db.session.add(script)
    db.session.commit()

    assert len(script.image_prompt) > 100


def test_create_script_camera(client):
    """创建视频分镜"""
    novel = Novel(name="测试", original_text="内容")
    db.session.add(novel)
    db.session.commit()

    project = Project(name="项目", novel_id=novel.id, mode="camera")
    db.session.add(project)
    db.session.commit()

    script = ScriptCamera(
        project_id=project.id,
        shot_index=1,
        content="镜头描述",
        first_frame_path="/path/to/first.png",
        last_frame_path="/path/to/last.png"
    )
    db.session.add(script)
    db.session.commit()

    assert script.first_frame_path.endswith(".png")
