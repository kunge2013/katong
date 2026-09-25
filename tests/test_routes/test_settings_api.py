# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import pytest


# [AGC:START] tool=Cc author=fangkun
def test_list_settings_empty(client):
    """空列表"""
    response = client.get('/api/settings')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data'] == []


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_create_and_list_setting(client):
    """创建并列出设置"""
    # 创建
    response = client.put('/api/settings/zhihu_cookie',
                          json={"value": "test-cookie-value", "encrypted": True})
    assert response.status_code in (200, 201)
    # 列出
    response = client.get('/api/settings')
    data = response.get_json()
    assert len(data['data']) == 1
    assert data['data'][0]['key'] == 'zhihu_cookie'
    assert data['data'][0]['value'] == 'v2:***'  # 脱敏


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_reject_unknown_key(client):
    """拒绝不在白名单的 key"""
    response = client.put('/api/settings/unknown_key',
                          json={"value": "test", "encrypted": False})
    assert response.status_code == 400


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_delete_setting(client):
    """删除设置"""
    client.put('/api/settings/zhihu_cookie',
               json={"value": "test", "encrypted": True})
    response = client.delete('/api/settings/zhihu_cookie')
    assert response.status_code == 200
    response = client.get('/api/settings')
    assert len(response.get_json()['data']) == 0


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_delete_nonexistent(client):
    """删除不存在的设置"""
    response = client.delete('/api/settings/nope')
    assert response.status_code == 404


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_zhihu_status_no_cookie(client):
    """知乎状态 - 未登录"""
    response = client.get('/api/settings/zhihu/status')
    assert response.status_code == 200
    data = response.get_json()
    assert data['data']['logged_in'] is False


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_zhihu_status_with_cookie(client):
    """知乎状态 - 已登录"""
    client.put('/api/settings/zhihu_cookie',
               json={"value": "test-cookie", "encrypted": True})
    response = client.get('/api/settings/zhihu/status')
    data = response.get_json()
    assert data['data']['logged_in'] is True
    assert data['data']['has_cookie'] is True


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_update_existing_setting(client):
    """更新已存在的设置"""
    client.put('/api/settings/zhihu_cookie',
               json={"value": "old-value", "encrypted": True})
    client.put('/api/settings/zhihu_cookie',
               json={"value": "new-value", "encrypted": True})
    response = client.get('/api/settings')
    data = response.get_json()
    assert len(data['data']) == 1


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_zhihu_login_not_implemented(client, app, monkeypatch):
    """知乎登录 - zhihu_downloader 抛出异常时返回 501/500"""
    # 模拟 zhihu_downloader 不存在（Task 3 未完成的场景）
    import sys
    # 临时移除 zhihu_downloader 模块，模拟 ImportError
    saved = sys.modules.pop("cinegacha.services.zhihu_downloader", None)
    sys.modules["cinegacha.services.zhihu_downloader"] = None  # type: ignore
    try:
        response = client.post('/api/settings/zhihu/login')
        assert response.status_code in (501, 500)
        data = response.get_json()
        assert data['success'] is False
    finally:
        # 恢复模块
        if saved is not None:
            sys.modules["cinegacha.services.zhihu_downloader"] = saved
        else:
            sys.modules.pop("cinegacha.services.zhihu_downloader", None)


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_zhihu_login_success(client, app, monkeypatch):
    """知乎登录 - 成功时保存 cookie"""
    import cinegacha.services.zhihu_downloader as zd
    monkeypatch.setattr(zd, "start_browser_login", lambda timeout=300: "fake-z_c0-cookie")
    response = client.post('/api/settings/zhihu/login')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    # 验证 cookie 已保存
    from cinegacha.services.settings_service import SettingsService
    service = SettingsService()
    assert service.get("zhihu_cookie") == "fake-z_c0-cookie"


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_create_plain_setting(client):
    """创建明文设置"""
    response = client.put('/api/settings/zhihu_user_agent',
                          json={"value": "Mozilla/5.0", "encrypted": False})
    assert response.status_code in (200, 201)
    response = client.get('/api/settings')
    data = response.get_json()
    item = next(s for s in data['data'] if s['key'] == 'zhihu_user_agent')
    assert item['is_encrypted'] == 0
    assert item['value'] == 'Mozi...'  # 明文脱敏：前 4 字符 + ...


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_zhihu_status_with_user_agent_only(client):
    """知乎状态 - 只有 user_agent 无 cookie 时未登录"""
    client.put('/api/settings/zhihu_user_agent',
               json={"value": "Mozilla/5.0", "encrypted": False})
    response = client.get('/api/settings/zhihu/status')
    data = response.get_json()
    assert data['data']['logged_in'] is False
    assert data['data']['has_cookie'] is False


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_put_missing_body(client):
    """PUT 缺少请求体"""
    response = client.put('/api/settings/zhihu_cookie',
                          content_type='application/json')
    assert response.status_code == 400


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def test_put_missing_value(client):
    """PUT 缺少 value 字段"""
    response = client.put('/api/settings/zhihu_cookie',
                          json={"encrypted": True})
    assert response.status_code == 400


# [AGC:END]
