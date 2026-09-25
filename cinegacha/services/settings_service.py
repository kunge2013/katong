# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from typing import Optional
from flask import current_app
from cinegacha import db
from cinegacha.models.settings import Setting
from cinegacha.services.crypto import CryptoService


# [AGC:START] tool=Cc author=fangkun
class SettingsService:
    """系统配置管理服务，支持 Fernet 加密存储"""

    def __init__(self) -> None:
        fernet_key: Optional[str] = current_app.config.get("FERNET_KEY")
        self._crypto = CryptoService(key=fernet_key)

    def get(self, key: str) -> Optional[str]:
        """
        读取配置值，加密的自动解密。不存在返回 None

        Args:
            key: 配置键名

        Returns:
            配置值（解密后的明文）或 None
        """
        setting = db.session.query(Setting).filter_by(key=key).first()
        if setting is None:
            return None

        if setting.is_encrypted == 1 and setting.value:
            return self._crypto.decrypt(setting.value)
        return setting.value

    def set(self, key: str, value: str, encrypted: bool = True) -> Setting:
        """
        写入配置值。encrypted=True 时自动 Fernet 加密。upsert（存在则更新，不存在则插入）

        Args:
            key: 配置键名
            value: 配置值
            encrypted: 是否加密存储

        Returns:
            创建或更新的 Setting 实例
        """
        stored_value: str = value
        is_encrypted_flag: int = 1 if encrypted else 0

        if encrypted and value:
            stored_value = self._crypto.encrypt(value)

        setting = db.session.query(Setting).filter_by(key=key).first()
        if setting is None:
            setting = Setting(
                key=key,
                value=stored_value,
                is_encrypted=is_encrypted_flag,
            )
            db.session.add(setting)
        else:
            setting.value = stored_value
            setting.is_encrypted = is_encrypted_flag

        db.session.commit()
        return setting

    def delete(self, key: str) -> bool:
        """
        删除配置，不存在返回 False

        Args:
            key: 配置键名

        Returns:
            是否成功删除
        """
        setting = db.session.query(Setting).filter_by(key=key).first()
        if setting is None:
            return False

        db.session.delete(setting)
        db.session.commit()
        return True

    def get_all(self) -> list[dict]:
        """
        列出所有配置。加密值脱敏为 'v2:***'。

        Returns:
            [{key, value, is_encrypted, updated_at}]
        """
        settings = db.session.query(Setting).all()
        result: list[dict] = []
        for s in settings:
            result.append({
                "key": s.key,
                "value": self.mask_value(s.value, s.is_encrypted),
                "is_encrypted": s.is_encrypted,
                "updated_at": s.updated_at,
            })
        return result

    def mask_value(self, value: str, is_encrypted: int) -> str:
        """
        脱敏显示：加密值显示为 'v2:***'，明文值截取前 4 字符 + '...'

        Args:
            value: 原始值
            is_encrypted: 是否加密 (1/0)

        Returns:
            脱敏后的显示值
        """
        if is_encrypted == 1:
            return "v2:***"

        if value is None:
            return "..."

        return f"{value[:4]}..."

# [AGC:END]
