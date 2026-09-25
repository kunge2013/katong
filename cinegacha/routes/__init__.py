# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

def register_blueprints(app):
    """注册所有 blueprints"""
    from cinegacha.routes.novel import novel_bp
    app.register_blueprint(novel_bp)
