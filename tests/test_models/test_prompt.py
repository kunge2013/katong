# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from cinegacha import db
from cinegacha.models.prompt import Prompt


def test_create_prompt(client):
    """创建提示词模板"""
    prompt = Prompt(
        title="提取角色描述",
        category="角色设定",
        content="v2:gAAAAAB..."  # 加密内容
    )
    db.session.add(prompt)
    db.session.commit()

    assert prompt.id is not None
    assert prompt.category == "角色设定"
    assert prompt.content.startswith("v2:")
