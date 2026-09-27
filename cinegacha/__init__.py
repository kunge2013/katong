# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base


# 使用纯 SQLAlchemy declarative base
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

db = SQLAlchemy()


def create_app(config_name: str = "development") -> Flask:
    """Flask app factory"""
    app = Flask(__name__, template_folder='templates', static_folder='static')

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
    with app.app_context():
        # 导入模型以确保它们被注册
        from cinegacha.models import novel, project, role, script, prompt, settings

        from cinegacha.routes import register_blueprints
        register_blueprints(app)

        # 创建数据库表
        Base.metadata.create_all(bind=db.engine)

    # 注册错误处理器
    register_error_handlers(app)

    return app


def register_error_handlers(app):
    """注册错误处理器"""
    from flask import jsonify

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": {
                "code": "NOT_FOUND",
                "message": "资源不存在"
            }
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": "请求参数错误"
            }
        }), 400

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "服务器内部错误"
            }
        }), 500
