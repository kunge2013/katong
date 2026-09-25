# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25


def register_blueprints(app):
    """注册所有 blueprints"""
    from cinegacha.routes.novel import novel_bp
    from cinegacha.routes.role import role_bp
    from cinegacha.routes.script import script_bp
    from cinegacha.routes.settings import settings_bp
    from cinegacha.routes.web import web_bp
    app.register_blueprint(novel_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(script_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(web_bp)
