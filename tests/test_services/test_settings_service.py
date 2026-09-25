# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from cinegacha import db
from cinegacha.services.settings_service import SettingsService


# [AGC:START] tool=Cc author=fangkun
def test_set_and_get_encrypted(app):
    """加密设置和读取"""
    service = SettingsService()
    service.set("zhihu_cookie", "my-secret-cookie", encrypted=True)
    result = service.get("zhihu_cookie")
    assert result == "my-secret-cookie"


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_set_and_get_plain(app):
    """明文设置和读取"""
    service = SettingsService()
    service.set("app_name", "CineGacha", encrypted=False)
    result = service.get("app_name")
    assert result == "CineGacha"


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_get_nonexistent_returns_none(app):
    """读取不存在的 key 返回 None"""
    service = SettingsService()
    assert service.get("does_not_exist") is None


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_update_existing_key(app):
    """更新已存在的 key（upsert）"""
    service = SettingsService()
    service.set("key1", "value1")
    service.set("key1", "value2")
    assert service.get("key1") == "value2"
    # 确认只有一条记录
    from cinegacha.models.settings import Setting
    count = db.session.query(Setting).filter_by(key="key1").count()
    assert count == 1


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_delete_existing(app):
    """删除已存在的 key"""
    service = SettingsService()
    service.set("to_delete", "value")
    assert service.delete("to_delete") is True
    assert service.get("to_delete") is None


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_delete_nonexistent(app):
    """删除不存在的 key 返回 False"""
    service = SettingsService()
    assert service.delete("nope") is False


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_get_all_masks_encrypted(app):
    """get_all 对加密值脱敏"""
    service = SettingsService()
    service.set("secret", "top-secret", encrypted=True)
    service.set("public", "hello", encrypted=False)
    all_settings = service.get_all()
    secret_item = next(s for s in all_settings if s["key"] == "secret")
    public_item = next(s for s in all_settings if s["key"] == "public")
    assert secret_item["value"] == "v2:***"
    assert public_item["value"] == "hell..."  # 前 4 字符 + ...
    assert secret_item["is_encrypted"] == 1


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_mask_value_plain_short(app):
    """短明文不截取"""
    service = SettingsService()
    assert service.mask_value("abc", 0) == "abc..."  # 不足 4 字符也加 ...


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_mask_value_plain_long(app):
    """长明文截取前 4 字符"""
    service = SettingsService()
    assert service.mask_value("longvalue", 0) == "long..."


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_mask_value_encrypted(app):
    """加密值统一显示 v2:***"""
    service = SettingsService()
    assert service.mask_value("v2:gAAAAABxyz", 1) == "v2:***"


# [AGC:END]
