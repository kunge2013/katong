# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from typing import Any
from flask import Blueprint, request, jsonify
from cinegacha.services.settings_service import SettingsService

# [AGC:START] tool=Cc author=fangkun
settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')

# 允许的配置键白名单
ALLOWED_KEYS: frozenset[str] = frozenset({"zhihu_cookie", "zhihu_user_agent"})


# [AGC:START] tool=Cc author=fangkun
def _ok(data: Any = None, message: str | None = None) -> tuple:
    """统一成功响应"""
    payload: dict[str, Any] = {"success": True}
    if data is not None:
        payload["data"] = data
    if message is not None:
        payload["message"] = message
    return jsonify(payload)


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def _err(code: str, message: str, status: int = 400) -> tuple:
    """统一错误响应"""
    return jsonify({
        "success": False,
        "error": {"code": code, "message": message},
    }), status


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
@settings_bp.route('', methods=['GET'])
def list_settings():
    """列出所有配置（脱敏）"""
    try:
        service = SettingsService()
        items = service.get_all()
        return _ok(data=items)
    except Exception as e:
        return _err("LIST_ERROR", str(e), 500)


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
@settings_bp.route('/<key>', methods=['PUT'])
def upsert_setting(key: str):
    """
    创建或更新配置

    Request Body:
        {"value": "xxx", "encrypted": true|false}
    """
    if key not in ALLOWED_KEYS:
        return _err(
            "INVALID_KEY",
            f"不允许的配置键: {key}。允许的键: {', '.join(sorted(ALLOWED_KEYS))}",
        )

    data = request.get_json(silent=True)
    if not data:
        return _err("MISSING_BODY", "缺少请求体 JSON")
    if "value" not in data:
        return _err("MISSING_VALUE", "缺少 value 字段")

    value = data["value"]
    encrypted = bool(data.get("encrypted", True))

    try:
        service = SettingsService()
        existing = service.get(key)
        setting = service.set(key, value, encrypted=encrypted)
        status = 200 if existing is not None else 201
        return _ok(
            data={
                "key": setting.key,
                "is_encrypted": setting.is_encrypted,
                "updated_at": setting.updated_at.isoformat() if setting.updated_at else None,
            },
            message="更新成功" if existing is not None else "创建成功",
        ), status
    except Exception as e:
        return _err("UPSERT_ERROR", str(e), 500)


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
@settings_bp.route('/<key>', methods=['DELETE'])
def delete_setting(key: str):
    """删除配置"""
    try:
        service = SettingsService()
        deleted = service.delete(key)
        if not deleted:
            return _err("NOT_FOUND", f"配置不存在: {key}", 404)
        return _ok(message="删除成功")
    except Exception as e:
        return _err("DELETE_ERROR", str(e), 500)


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
@settings_bp.route('/zhihu/status', methods=['GET'])
def zhihu_status():
    """知乎登录状态"""
    try:
        service = SettingsService()
        cookie = service.get("zhihu_cookie")
        has_cookie = cookie is not None and cookie != ""
        # TODO: 实际检查登录状态需要 HTTP 调用，暂时用 has_cookie 替代
        logged_in = has_cookie

        cookie_preview = service.mask_value(
            # 拿加密后的原始值做脱敏预览
            _get_raw_value("zhihu_cookie"),
            1,
        ) if has_cookie else None

        return _ok(data={
            "logged_in": logged_in,
            "has_cookie": has_cookie,
            "cookie_preview": cookie_preview,
        })
    except Exception as e:
        return _err("STATUS_ERROR", str(e), 500)


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
def _get_raw_value(key: str) -> str:
    """读取数据库中的原始存储值（不解密）"""
    from cinegacha import db
    from cinegacha.models.settings import Setting
    setting = db.session.query(Setting).filter_by(key=key).first()
    return setting.value if setting and setting.value else ""


# [AGC:END]


# [AGC:START] tool=Cc author=fangkun
@settings_bp.route('/zhihu/login', methods=['POST'])
def zhihu_login():
    """触发 Playwright 浏览器登录知乎"""
    try:
        from cinegacha.services.zhihu_downloader import start_browser_login
        cookie = start_browser_login()
        service = SettingsService()
        service.set("zhihu_cookie", cookie, encrypted=True)
        return _ok(message="登录成功")
    except ImportError:
        return _err("NOT_IMPLEMENTED", "Playwright 未安装", 501)
    except Exception as e:
        return _err("LOGIN_FAILED", str(e), 500)


# [AGC:END]

# [AGC:END]
