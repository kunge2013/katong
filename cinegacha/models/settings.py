# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from sqlalchemy import Column, Integer, String, Text
from cinegacha import Base
from cinegacha.models.base import TimestampMixin


class Setting(TimestampMixin, Base):
    """系统配置表（部分 Fernet 加密）"""
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text)  # 敏感值加密: v2:gAAAAAB...
    is_encrypted = Column(Integer, default=0)
