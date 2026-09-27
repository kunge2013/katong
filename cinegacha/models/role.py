# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from cinegacha import Base
from cinegacha.models.base import TimestampMixin


class Role(TimestampMixin, Base):
    """资产表（角色/场景/道具统一存储）"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    novel_id = Column(Integer, ForeignKey("novels.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))

    # 双层描述
    content = Column(Text)  # 中文基础描述 (37-250字)
    content_word2 = Column(Text)  # 英文增强描述 (可选)

    # 资产 URL
    cover_url = Column(String(500))  # 封面图
    role_url = Column(String(500))  # 云端参考图 (签名 URL, 72h)
    reference_image_url = Column(String(500))  # 本地参考图
    portrait_preview_json = Column(Text)  # 肖像预览 (JSON)

    # 元数据
    role_kind = Column(String(50), default="library")
    asset_art_style_json = Column(Text)  # 艺术风格 (JSON)

    # 关系
    tags = relationship("RoleTag", back_populates="role", cascade="all, delete-orphan")


class RoleTag(Base):
    """资产标签表"""
    __tablename__ = "role_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    tag_category = Column(String(50), nullable=False)  # '性别' | '时代' | '小说' | '类型'
    tag_value = Column(String(100), nullable=False)  # '男' | '古代' | '角色' | '场景' | '道具'

    # 关系
    role = relationship("Role", back_populates="tags")
