"""集成测试 — 报到路由"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.schemas.registration import RegistrationCreate

client = TestClient(app)


class TestCreateRegistration:

    def test_正常提交返回201(self, mock_student_token):
        data = self._payload("20260001")
        resp = client.post("/student/registration", json=data,
                           headers={"Authorization": f"Bearer {mock_student_token}"})
        assert resp.status_code == 201
        assert resp.json()["status"] == "SUBMITTED"

    def test_重复提交返回409(self, mock_student_token):
        data = self._payload("20260002")
        client.post("/student/registration", json=data,
                    headers={"Authorization": f"Bearer {mock_student_token}"})
        resp = client.post("/student/registration", json=data,
                           headers={"Authorization": f"Bearer {mock_student_token}"})
        assert resp.status_code == 409

    def test_字段缺失返回422(self, mock_student_token):
        resp = client.post("/student/registration", json={"name": "张三"},
                           headers={"Authorization": f"Bearer {mock_student_token}"})
        assert resp.status_code == 422

    def test_身份证格式错误返回422(self, mock_student_token):
        data = self._payload("20260003")
        data["id_number"] = "123456"
        resp = client.post("/student/registration", json=data,
                           headers={"Authorization": f"Bearer {mock_student_token}"})
        assert resp.status_code == 422

    def test_未提交时GET返回404(self, mock_student_token):
        resp = client.get("/student/registration",
                          headers={"Authorization": f"Bearer {mock_student_token}"})
        assert resp.status_code == 404

    @staticmethod
    def _payload(student_id: str) -> dict:
        return RegistrationCreate(
            name="张三", student_id=student_id, college="计算机学院",
            class_name="2026计算机1班", building="A1栋", phone="13800138000",
            id_number="110101200001011234", emergency_contact="李四",
            emergency_phone="13900139000", enrollment_date="2026-09-01",
        ).model_dump(mode="json")


class TestGetAndUpdateRegistration:

    def test_提交后可查询(self, mock_student_token):
        data = RegistrationCreate(
            name="张三", student_id="20260004", college="计算机学院",
            class_name="2026计算机1班", building="A1栋", phone="13800138000",
            id_number="110101200001011234", emergency_contact="李四",
            emergency_phone="13900139000", enrollment_date="2026-09-01",
        ).model_dump(mode="json")
        client.post("/student/registration", json=data,
                    headers={"Authorization": f"Bearer {mock_student_token}"})
        resp = client.get("/student/registration",
                          headers={"Authorization": f"Bearer {mock_student_token}"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "SUBMITTED"


class TestUnauthenticated:

    def test_无token返回401(self):
        resp = client.get("/student/registration")
        assert resp.status_code == 401
