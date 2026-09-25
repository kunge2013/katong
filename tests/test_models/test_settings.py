# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from cinegacha import db
from cinegacha.models.settings import Setting


def test_create_setting(client):
    """创建配置"""
    setting = Setting(
        key="manga_image_provider",
        value="grsai",
        is_encrypted=0
    )
    db.session.add(setting)
    db.session.commit()

    assert setting.key == "manga_image_provider"


def test_encrypted_setting(client):
    """加密配置"""
    setting = Setting(
        key="account_pool_deepseek_api_key",
        value="v2:gAAAAAB...",
        is_encrypted=1
    )
    db.session.add(setting)
    db.session.commit()

    assert setting.is_encrypted == 1
