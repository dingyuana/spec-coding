"""JWT 工具 + 密码哈希"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone, timedelta
import jwt
from src.core.config import settings


def create_access_token(
    sub: str,
    role: str,
    expires_in: int = None,
    **kwargs,
) -> str:
    """签发 JWT token。payload = { sub, role, exp, ... }"""
    minutes = expires_in if expires_in is not None else settings.jwt_expire_minutes
    exp = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload = {"sub": sub, "role": role, "exp": exp}
    payload.update(kwargs)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """解码 JWT token，过期或无效抛出 jwt.ExpiredSignatureError / jwt.InvalidTokenError"""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if "exp" not in payload:
            raise jwt.InvalidTokenError("missing exp")
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.DecodeError):
        raise


def hash_password(password: str) -> str:
    """SHA-256 加盐哈希。格式: salt:hash (十六进制)"""
    salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{digest}"


def verify_password(plain: str, hashed: str) -> bool:
    """验证密码。hashed 格式: salt:hash"""
    try:
        salt, expected = hashed.split(":", 1)
    except ValueError:
        return False
    actual = hashlib.sha256((salt + plain).encode()).hexdigest()
    return secrets.compare_digest(actual, expected)


def _exchange_code(code: str) -> dict:
    """mock 微信 code 换取 openid + session_key"""
    if not code or len(code) < 4:
        return {"openid": None}
    return {"openid": f"openid-{code}", "session_key": f"sk-{code}"}
