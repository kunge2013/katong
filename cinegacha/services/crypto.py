# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

from cryptography.fernet import Fernet
import base64
import os
from typing import Optional


class CryptoService:
    """Fernet 加密服务"""

    def __init__(self, key: Optional[str] = None):
        """
        初始化加密服务

        Args:
            key: Fernet 密钥（32 字节 base64 编码）。如果为 None，从环境变量 FERNET_KEY 读取
        """
        if key is None:
            key = os.environ.get("FERNET_KEY")

        if key is None:
            raise ValueError("FERNET_KEY 未配置，请设置环境变量或传入 key 参数")

        # 确保密钥长度正确（32 字节）
        if len(key) < 32:
            key = key.ljust(32, "=")
        elif len(key) > 32:
            key = key[:32]

        # 转换为 base64 编码
        key_bytes = base64.urlsafe_b64encode(key.encode("utf-8"))
        self._fernet = Fernet(key_bytes)

    def encrypt(self, plaintext: str) -> str:
        """
        加密文本

        Args:
            plaintext: 明文

        Returns:
            加密后的文本（带 v2: 前缀）
        """
        encrypted = self._fernet.encrypt(plaintext.encode("utf-8"))
        return f"v2:{encrypted.decode('utf-8')}"

    def decrypt(self, encrypted_text: str) -> str:
        """
        解密文本

        Args:
            encrypted_text: 加密文本（带 v2: 前缀）

        Returns:
            解密后的明文
        """
        if not encrypted_text.startswith("v2:"):
            raise ValueError("加密文本格式错误，缺少 v2: 前缀")

        encrypted_bytes = encrypted_text[3:].encode("utf-8")
        decrypted = self._fernet.decrypt(encrypted_bytes)
        return decrypted.decode("utf-8")

    def is_encrypted(self, text: str) -> bool:
        """检查文本是否已加密"""
        return text.startswith("v2:") if text else False
