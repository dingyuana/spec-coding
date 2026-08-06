"""FastAPI 依赖注入 — get_current_*"""
from __future__ import annotations

from typing import Optional

from fastapi import Header, HTTPException
from fastapi.security import HTTPBearer
from src.core.auth.utils import decode_access_token

security = HTTPBearer()


def _get_payload(authorization: Optional[str]) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未授权")
    token = authorization[7:]
    try:
        return decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")


def get_current_payload(authorization: str = Header(None)) -> dict:
    return _get_payload(authorization)


def get_current_student(authorization: str = Header(None)) -> dict:
    payload = _get_payload(authorization)
    if payload.get("role") != "student":
        raise HTTPException(status_code=403, detail="需要学生权限")
    return payload


def get_current_admin(authorization: str = Header(None)) -> dict:
    payload = _get_payload(authorization)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return payload


def get_current_counselor(authorization: str = Header(None)) -> dict:
    payload = _get_payload(authorization)
    if payload.get("role") != "counselor":
        raise HTTPException(status_code=403, detail="需要辅导员权限")
    if "class_name" not in payload or "college" not in payload:
        raise HTTPException(status_code=401, detail="令牌信息不完整")
    return payload
