# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from sqlalchemy import Column, Integer, String, Text
from cinegacha import Base
from cinegacha.models.base import TimestampMixin


class Novel(TimestampMixin, Base):
    """小说表"""
    __tablename__ = "novels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    content = Column(Text)  # 清洗后文本
    original_text = Column(Text, default="")  # 原始文本
    character_text = Column(Text, default="")  # 角色提取文本
    revised_text = Column(Text, default="")  # 修订后文本
    script_text = Column(Text, default="")  # 剧本化文本
    storyboard_text = Column(Text, default="")  # 分镜文本
    opening_text = Column(Text, default="")  # 开头文本

    # 来源
    share_url = Column(String(500), default="")
    word_count = Column(Integer, default=0)

    # 清洗状态
    is_format_cleaned = Column(Integer, default=0)
    is_serial_cleaned = Column(Integer, default=0)
    is_punct_cleaned = Column(Integer, default=0)
    is_shot_cleaned = Column(Integer, default=0)  # 待实现

    # 评分
    score_value = Column(Integer)
    score_report = Column(Text)
