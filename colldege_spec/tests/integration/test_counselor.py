"""集成测试 — 辅导员端路由（COUN-S1~S6）"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.schemas.registration import RegistrationCreate

client = TestClient(app)


def _create_student(student_token: str, student_id: str, class_name: str) -> int:
    payload = RegistrationCreate(
        name="张三", student_id=student_id, college="计算机学院",
        class_name=class_name, building="A1栋", phone="13800138000",
        id_number="110101200001011234", emergency_contact="李四",
        emergency_phone="13900139000", enrollment_date="2026-09-01",
    ).model_dump(mode="json")
    r = client.post("/student/registration", json=payload,
                    headers={"Authorization": f"Bearer {student_token}"})
    assert r.status_code == 201, f"expected 201 got {r.status_code}: {r.text[:200]}"
    return r.json()["id"]


class TestCounselorLogin:

    def test_辅导员登录成功(self):
        resp = client.post("/auth/counselor", json={"username": "counselor01", "password": "counselor123"})
        assert resp.status_code == 200
        assert "token" in resp.json()


class TestCounselorStudents:

    def test_查看本班列表(self, mock_counselor_token, mock_student_token):
        _create_student(mock_student_token, "20262001", "2026计算机1班")
        resp = client.get("/counselor/students",
                          headers={"Authorization": f"Bearer {mock_counselor_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data


class TestCounselorAudit:

    def test_审核通过(self, mock_counselor_token, mock_student_token):
        sid = _create_student(mock_student_token, "20262002", "2026计算机1班")
        resp = client.post(f"/counselor/audit/{sid}", json={"action": "APPROVED"},
                           headers={"Authorization": f"Bearer {mock_counselor_token}"})
        assert resp.status_code == 200

    def test_审核驳回(self, mock_counselor_token, mock_student_token):
        sid = _create_student(mock_student_token, "20262003", "2026计算机1班")
        resp = client.post(f"/counselor/audit/{sid}",
                           json={"action": "REJECTED", "reason": "身份证格式错误"},
                           headers={"Authorization": f"Bearer {mock_counselor_token}"})
        assert resp.status_code == 200

    def test_驳回无reason返回400(self, mock_counselor_token, mock_student_token):
        sid = _create_student(mock_student_token, "20262004", "2026计算机1班")
        resp = client.post(f"/counselor/audit/{sid}", json={"action": "REJECTED"},
                           headers={"Authorization": f"Bearer {mock_counselor_token}"})
        assert resp.status_code == 400

    def test_越权审核返回403(self, mock_counselor_token_other_class, mock_student_token, mock_counselor_token):
        sid = _create_student(mock_student_token, "20262005", "2026计算机2班")
        resp = client.post(f"/counselor/audit/{sid}", json={"action": "APPROVED"},
                           headers={"Authorization": f"Bearer {mock_counselor_token}"})
        assert resp.status_code == 403


class TestCounselorDashboard:

    def test_看板(self, mock_counselor_token):
        resp = client.get("/counselor/dashboard",
                          headers={"Authorization": f"Bearer {mock_counselor_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "class_name" in data
        assert "total_count" in data
        assert "by_status" in data
