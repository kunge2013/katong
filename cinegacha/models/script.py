# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from cinegacha import Base
from cinegacha.models.base import TimestampMixin


class Script(TimestampMixin, Base):
    """分镜表（manga 模式）"""
    __tablename__ = "scripts_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    shot_id = Column(Integer)
    shot_index = Column(Integer, nullable=False)  # 排序索引

    # 内容
    content = Column(Text)  # 分镜文本
    presets = Column(Text)  # 出场资产 JSON ["明溪", "明家祠堂夜晚", "婚书"]
    image_prompt = Column(Text)  # 图像提示词 (455-1270字)
    video_prompt = Column(Text)
    screen_prompt = Column(Text)

    # 图像
    main_image = Column(String(500))  # 生成的图像路径
    candidate_images = Column(Text)  # 候选图 JSON


class ScriptCamera(TimestampMixin, Base):
    """分镜表（camera 模式）"""
    __tablename__ = "scripts_camera"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    shot_index = Column(Integer, nullable=False)

    content = Column(Text)
    image_prompt = Column(Text)

    # 视频帧
    first_frame_path = Column(String(500))
    last_frame_path = Column(String(500))
