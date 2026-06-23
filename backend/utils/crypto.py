"""Cookie加密存储 - AES-256-GCM"""
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64

from config.settings import settings


def encrypt_cookie(data: dict) -> str:
    """
    将Cookie数据加密存储

    Args:
        data: 原始Cookie字典

    Returns:
        加密后的Base64字符串（包含IV）
    """
    plaintext = base64.b64encode(json.dumps(data).encode("utf-8"))
    key = AESGCM.from_bytes(bytes.fromhex(settings.encryption_key[:64]))
    nonce = os.urandom(12)
    ciphertext = key.encrypt(nonce, plaintext, None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")


def decrypt_cookie(encrypted: str) -> dict:
    """
    解密Cookie数据

    Args:
        encrypted: 加密后的Base64字符串

    Returns:
        原始Cookie字典
    """
    decoded = base64.b64decode(encrypted)
    nonce = decoded[:12]
    ciphertext = decoded[12:]
    key = AESGCM.from_bytes(bytes.fromhex(settings.encryption_key[:64]))
    plaintext = key.decrypt(nonce, ciphertext, None)
    return json.loads(base64.b64decode(plaintext).decode("utf-8"))
