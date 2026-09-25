# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import pytest
from cinegacha.services.crypto import CryptoService


@pytest.fixture
def crypto():
    """创建加密服务实例"""
    return CryptoService(key="test-fernet-key-must-be-32-bytes")


def test_encrypt_decrypt(crypto):
    """加密和解密"""
    plaintext = "sk-1234567890abcdef"
    encrypted = crypto.encrypt(plaintext)

    # 加密后应该有 v2: 前缀
    assert encrypted.startswith("v2:")
    assert encrypted != plaintext

    # 解密应该得到原文
    decrypted = crypto.decrypt(encrypted)
    assert decrypted == plaintext


def test_encrypt_chinese(crypto):
    """加密中文"""
    plaintext = "这是一段中文提示词"
    encrypted = crypto.encrypt(plaintext)
    decrypted = crypto.decrypt(encrypted)

    assert decrypted == plaintext


def test_decrypt_invalid_format(crypto):
    """解密格式错误的文本"""
    with pytest.raises(ValueError, match="缺少 v2: 前缀"):
        crypto.decrypt("invalid-encrypted-text")


def test_is_encrypted(crypto):
    """检查是否已加密"""
    encrypted = crypto.encrypt("test")
    assert crypto.is_encrypted(encrypted) is True
    assert crypto.is_encrypted("plaintext") is False
    assert crypto.is_encrypted("") is False


def test_missing_key():
    """缺少密钥"""
    import os
    original_key = os.environ.get("FERNET_KEY")
    if "FERNET_KEY" in os.environ:
        del os.environ["FERNET_KEY"]

    try:
        with pytest.raises(ValueError, match="FERNET_KEY 未配置"):
            CryptoService()
    finally:
        if original_key:
            os.environ["FERNET_KEY"] = original_key
