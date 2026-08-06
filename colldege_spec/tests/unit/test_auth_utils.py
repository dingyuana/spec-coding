"""单元测试 — AuthUtils（JWT 签发/验证 + 密码哈希）"""
import pytest
from src.core.auth.utils import create_access_token, decode_access_token, hash_password, verify_password


class TestCreateToken:
    def test_token_含_required_claims(self):
        """AUTH-S1: JWT token 必须含 sub/role/exp 三个必填字段"""
        token = create_access_token(sub="test-openid", role="student")
        payload = decode_access_token(token)
        assert "sub" in payload
        assert "role" in payload
        assert "exp" in payload

    def test_token_含正确_role(self):
        """AUTH-S1: 不同角色签发对应 token"""
        token = create_access_token(sub="admin-001", role="admin")
        payload = decode_access_token(token)
        assert payload["role"] == "admin"

    def test_token_过期后无法解码(self):
        """AUTH-S8: 过期 token 解码失败"""
        import time
        token = create_access_token(sub="test", role="student", expires_in=-1)
        with pytest.raises(Exception):
            decode_access_token(token)


class TestPassword:
    def test_hash_password_返回盐值哈希格式(self):
        """密码哈希必须是 salt:hash 格式"""
        hashed = hash_password("test123")
        parts = hashed.split(":", 1)
        assert len(parts) == 2
        assert len(parts[0]) > 0   # salt
        assert len(parts[1]) == 64  # sha256 hex

    def test_same_password_不同哈希(self):
        """同一密码两次哈希结果不同（加随机 salt）"""
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2

    def test_verify_password_正确(self):
        """AUTH-S3/S6: 正确密码验证通过"""
        hashed = hash_password("real_password")
        assert verify_password("real_password", hashed) is True

    def test_verify_password_错误(self):
        """AUTH-S4/S7: 错误密码验证失败"""
        hashed = hash_password("real_password")
        assert verify_password("wrong_password", hashed) is False

    def test_verify_password_空字符串(self):
        """边界条件：空密码"""
        hashed = hash_password("test")
        assert verify_password("", hashed) is False
