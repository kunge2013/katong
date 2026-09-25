# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from cinegacha import db


class TimestampMixin:
    """时间戳 mixin"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
