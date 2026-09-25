# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import pytest
from cinegacha import create_app, db


@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """测试客户端"""
    return app.test_client()
