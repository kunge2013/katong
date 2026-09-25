# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import os
from pathlib import Path


class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # 数据库
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    DATA_DIR.mkdir(exist_ok=True)
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATA_DIR / 'cinegacha.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Fernet 加密密钥
    FERNET_KEY = os.environ.get("FERNET_KEY")

    # 输出目录
    OUTPUT_DIR = BASE_DIR / "Output"
    OUTPUT_DIR.mkdir(exist_ok=True)


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # 使用内存数据库
    FERNET_KEY = "test-fernet-key-must-be-32-bytes-long!!"  # 测试用固定密钥
