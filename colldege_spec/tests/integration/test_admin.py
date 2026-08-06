"""集成测试 — 管理端路由（ADM-S1~S9）"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.schemas.registration import RegistrationCreate

client = TestClient(app)


def _create_student(student_token: str, student_id: str) -> int:
    payload = RegistrationCreate(
        name="张三", student_id=student_id, college="计算机学院",
        class_name="2026计算机1班", building="A1栋", phone="13800138000",
        id_number="110101200001011234", emergency_contact="李四",
        emergency_phone="13900139000", enrollment_date="2026-09-01",
    ).model_dump(mode="json")
    r = client.post("/student/registration", json=payload,
                    headers={"Authorization": f"Bearer {student_token}"})
    assert r.status_code == 201, f"expected 201, got {r.status_code}"
    return r.json()["id"]


class TestAdminLogin:

    def test_管理员登录(self):
        resp = client.post("/auth/admin", json={"username": "admin", "password": "admin123"})
        assert resp.status_code == 200
        assert "token" in resp.json()


class TestAdminStudents:

    def test_查看全局列表(self, mock_admin_token, mock_student_token):
        _create_student(mock_student_token, "20261001")
        resp = client.get("/admin/students", headers={"Authorization": f"Bearer {mock_admin_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data

    def test_按学院筛选(self, mock_admin_token):
        resp = client.get("/admin/students?college=计算机学院",
                          headers={"Authorization": f"Bearer {mock_admin_token}"})
        assert resp.status_code == 200


class TestAdminAudit:

    def test_审核通过(self, mock_admin_token, mock_student_token):
        sid = _create_student(mock_student_token, "20261002")
        resp = client.post(f"/admin/audit/{sid}", json={"action": "APPROVED"},
                           headers={"Authorization": f"Bearer {mock_admin_token}"})
        assert resp.status_code == 200

    def test_审核驳回(self, mock_admin_token, mock_student_token):
        sid = _create_student(mock_student_token, "20261003")
        resp = client.post(f"/admin/audit/{sid}", json={"action": "REJECTED", "reason": "学号格式错误"},
                           headers={"Authorization": f"Bearer {mock_admin_token}"})
        assert resp.status_code == 200

    def test_驳回无reason(self, mock_admin_token, mock_student_token):
        sid = _create_student(mock_student_token, "20261004")
        resp = client.post(f"/admin/audit/{sid}", json={"action": "REJECTED"},
                           headers={"Authorization": f"Bearer {mock_admin_token}"})
        assert resp.status_code == 400


class TestAdminExport:

    def test_导出CSV(self, mock_admin_token, mock_student_token):
        _create_student(mock_student_token, "20261005")
        resp = client.get("/admin/export", headers={"Authorization": f"Bearer {mock_admin_token}"})
        assert resp.status_code == 200
        assert "text/csv" in resp.headers.get("Content-Type", "")


class TestAdminDashboard:

    def test_全局看板(self, mock_admin_token):
        resp = client.get("/admin/dashboard", headers={"Authorization": f"Bearer {mock_admin_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "today_count" in data
        assert "total_count" in data
        assert "by_status" in data
        assert "by_college" in data


class TestAdminLogs:

    def test_操作日志(self, mock_admin_token):
        resp = client.get("/admin/logs", headers={"Authorization": f"Bearer {mock_admin_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data


class TestAdminCounselors:

    def test_添加辅导员(self, mock_admin_token):
        resp = client.post("/admin/counselors",
                           json={"username": "new_counselor_001", "password": "pass123",
                                 "name": "李老师", "college": "计算机学院", "class_name": "2026计算机2班"},
                           headers={"Authorization": f"Bearer {mock_admin_token}"})
        assert resp.status_code == 201


class TestAdminPermission:

    def test_辅导员访问管理端返回403(self, mock_counselor_token):
        resp = client.get("/admin/students",
                          headers={"Authorization": f"Bearer {mock_counselor_token}"})
        assert resp.status_code == 403
