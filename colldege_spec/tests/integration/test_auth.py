"""集成测试 — 认证路由"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestStudentLogin:
    """微信学生登录（AUTH-S1, AUTH-S2）"""

    def test_valid_code_returns_token(self, monkeypatch):
        """AUTH-S1: 有效 code 返回 JWT token"""
        from src import main as main_mod
        original = main_mod._exchange_code
        main_mod._exchange_code = lambda code: {"openid": "test-openid-001", "session_key": "sk123"}
        response = client.post("/auth/student", json={"code": "valid-code"})
        main_mod._exchange_code = original
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "expires_in" in data

    def test_invalid_code_returns_401(self, monkeypatch):
        """AUTH-S2: 无效 code 返回 401"""
        from src import main as main_mod
        original = main_mod._exchange_code
        main_mod._exchange_code = lambda code: {"openid": None}
        response = client.post("/auth/student", json={"code": "invalid"})
        main_mod._exchange_code = original
        assert response.status_code == 401

    def test_missing_code_returns_401(self):
        """请求体缺少 code → 401（dict 接受，由业务层校验）"""
        response = client.post("/auth/student", json={})
        assert response.status_code == 401


class TestAdminLogin:
    """管理员登录（AUTH-S3, AUTH-S4, AUTH-S5）"""

    def test_valid_credentials_returns_token(self):
        """AUTH-S3: 正确密码返回 token"""
        response = client.post(
            "/auth/admin",
            json={"username": "admin", "password": "admin123"},
        )
        assert response.status_code == 200
        assert "token" in response.json()

    def test_wrong_password_returns_401(self):
        """AUTH-S4: 错误密码返回 401"""
        response = client.post(
            "/auth/admin",
            json={"username": "admin", "password": "wrong"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "用户名或密码错误"

    def test_nonexistent_user_returns_401(self):
        """AUTH-S5: 用户不存在返回 401，消息与 AUTH-S4 一致"""
        response = client.post(
            "/auth/admin",
            json={"username": "noexist", "password": "anything"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "用户名或密码错误"

    def test_token_payload_含role(self):
        """token payload 含 role=admin"""
        response = client.post(
            "/auth/admin",
            json={"username": "admin", "password": "admin123"},
        )
        token = response.json()["token"]
        from src.core.auth.utils import decode_access_token
        payload = decode_access_token(token)
        assert payload["role"] == "admin"


class TestCounselorLogin:
    """辅导员登录（COUN-S1）"""

    def test_valid_credentials_returns_token(self):
        """COUN-S1: 正确密码返回 token"""
        response = client.post(
            "/auth/counselor",
            json={"username": "counselor01", "password": "counselor123"},
        )
        assert response.status_code == 200
        assert "token" in response.json()

    def test_token_payload_含counselor_role(self):
        """COUN-S1: payload 含 role=counselor, class_name, college"""
        response = client.post(
            "/auth/counselor",
            json={"username": "counselor01", "password": "counselor123"},
        )
        token = response.json()["token"]
        from src.core.auth.utils import decode_access_token
        payload = decode_access_token(token)
        assert payload["role"] == "counselor"
        assert "class_name" in payload
        assert "college" in payload

    def test_wrong_password_returns_401(self):
        """AUTH-S7: 辅导员密码错误返回 401"""
        response = client.post(
            "/auth/counselor",
            json={"username": "counselor01", "password": "wrong"},
        )
        assert response.status_code == 401


class TestProtectedRoutes:
    """受保护接口（AUTH-S8）"""

    def test_invalid_token_returns_401(self):
        """AUTH-S8: 无效 token → 401"""
        response = client.get(
            "/student/registration",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    def test_missing_token_returns_401(self):
        """AUTH-S8: 缺少 token → 401"""
        response = client.get("/student/registration")
        assert response.status_code == 401
