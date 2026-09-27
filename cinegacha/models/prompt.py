# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from sqlalchemy import Column, Integer, String, Text
from cinegacha import Base
from cinegacha.models.base import TimestampMixin


class Prompt(TimestampMixin, Base):
    """提示词模板表（Fernet 加密）"""
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    category = Column(String(50))  # '角色设定' | '场景生成' | '对话生成'
    content = Column(Text, nullable=False)  # Fernet 加密: v2:gAAAAAB...
