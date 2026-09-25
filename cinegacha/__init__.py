# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


def create_app(config_name: str = "development") -> Flask:
    """Flask app factory"""
    app = Flask(__name__)

    # 加载配置
    if config_name == "testing":
        from cinegacha.config import TestingConfig
        app.config.from_object(TestingConfig)
    else:
        from cinegacha.config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)

    # 初始化扩展
    db.init_app(app)

    # 注册 blueprints
    from cinegacha.routes import register_blueprints
    register_blueprints(app)

    # 创建数据库表
    with app.app_context():
        db.create_all()

    return app
