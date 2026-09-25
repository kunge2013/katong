# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from cinegacha import db
from cinegacha.models.base import TimestampMixin


class Project(TimestampMixin, db.Model):
    """项目表"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    novel_id = Column(Integer, ForeignKey("novels.id"), nullable=False)
    mode = Column(String(50), default="manga")  # 'manga' | 'camera'

    # 画风配置
    manga_derive_preset_id = Column(String(100))
    img_prompt_prefix = Column(Text)
    img_prompt_suffix = Column(Text)

    # 模型配置 (JSON)
    manga_gen_models = Column(Text, default="{}")
