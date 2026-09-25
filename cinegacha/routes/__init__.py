# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from flask import Blueprint

# 创建 blueprints
novel_bp = Blueprint('novel', __name__, url_prefix='/api/novels')
project_bp = Blueprint('project', __name__, url_prefix='/api/projects')
role_bp = Blueprint('role', __name__, url_prefix='/api/roles')
script_bp = Blueprint('script', __name__, url_prefix='/api/scripts')
generate_bp = Blueprint('generate', __name__, url_prefix='/api/generate')
settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')


def register_blueprints(app):
    """注册所有 blueprints"""
    app.register_blueprint(novel_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(script_bp)
    app.register_blueprint(generate_bp)
    app.register_blueprint(settings_bp)
