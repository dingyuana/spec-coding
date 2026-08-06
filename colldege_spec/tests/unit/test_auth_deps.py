"""单元测试 — AuthDeps（依赖注入 / get_current_*）"""
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from src.main import app  # 暂不实现时导入会失败，这是预期的 RED


class TestGetCurrentStudent:
    """测试 get_current_student 依赖注入"""

    def test_有效token_返回openid(self, monkeypatch):
        """AUTH-S1: 学生 token 含正确 openid"""
        pass  # 待实现

    def test_无效token_抛出401(self, monkeypatch):
        """AUTH-S8: 无效 token 抛出 HTTPException(status_code=401)"""
        pass  # 待实现


class TestGetCurrentAdmin:
    """测试 get_current_admin 依赖注入"""

    def test_有效token_返回admin(self, monkeypatch):
        """AUTH-S3: admin token 通过"""
        pass  # 待实现

    def test_student_role_访问admin_抛出403(self, monkeypatch):
        """角色越权：学生 token 访问 admin 接口 → 403"""
        pass  # 待实现


class TestGetCurrentCounselor:
    """测试 get_current_counselor 依赖注入"""

    def test_有效token_返回counselor(self, monkeypatch):
        """AUTH-S6: counselor token 通过"""
        pass  # 待实现

    def test_counselor_payload_含class_name(self, monkeypatch):
        """COUN-S1: 辅导员 token payload 含 class_name 和 college"""
        pass  # 待实现
