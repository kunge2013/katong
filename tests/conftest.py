# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import pytest
from cinegacha import create_app, db, Base


@pytest.fixture(scope="session")
def app():
    """创建测试应用（会话级别）"""
    app = create_app("testing")
    with app.app_context():
        # 使用 Base.metadata 创建所有表
        Base.metadata.create_all(bind=db.engine)
        yield app
        Base.metadata.drop_all(bind=db.engine)


@pytest.fixture(scope="function")
def client(app):
    """测试客户端（函数级别）"""
    return app.test_client()


@pytest.fixture(scope="function", autouse=True)
def cleanup_db(app):
    """每个测试后清理数据库"""
    with app.app_context():
        yield
        # 清理所有表
        for table in reversed(Base.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
