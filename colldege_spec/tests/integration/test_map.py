"""集成测试 — 地图路由（MAP-S1~S4）"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestMapNearby:

    def test_获取附近建筑(self, mock_student_token):
        """MAP-S1: 返回附近建筑列表"""
        resp = client.get(
            "/map/nearby?lat=39.9&lng=116.4&radius=1000",
            headers={"Authorization": f"Bearer {mock_student_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "buildings" in data
        if data["buildings"]:
            b = data["buildings"][0]
            assert "name" in b
            assert "lat" in b
            assert "lng" in b
            assert "distance" in b

    def test_缺少坐标返回422(self, mock_student_token):
        """缺少 lat/lng → 422"""
        resp = client.get(
            "/map/nearby",
            headers={"Authorization": f"Bearer {mock_student_token}"},
        )
        assert resp.status_code == 422


class TestMapRoute:

    def test_计算完整路线(self, mock_student_token):
        """MAP-S2: 返回路径/距离/步行时间/步骤"""
        resp = client.get(
            "/map/route?from_lat=39.9&from_lng=116.4&to_lat=39.91&to_lng=116.41",
            headers={"Authorization": f"Bearer {mock_student_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "path" in data
        assert "distance" in data
        assert "walking_time" in data
        assert "steps" in data

    def test_路线含中文指引(self, mock_student_token):
        """MAP-S4: 路线步骤为中文"""
        resp = client.get(
            "/map/route?from_lat=39.9&from_lng=116.4&to_lat=39.91&to_lng=116.41",
            headers={"Authorization": f"Bearer {mock_student_token}"},
        )
        data = resp.json()
        assert len(data["steps"]) > 0
        assert "instruction" in data["steps"][0]


class TestMapBuildings:

    def test_获取建筑列表(self, mock_student_token):
        """MAP-S3: 返回校园建筑列表"""
        resp = client.get(
            "/map/buildings",
            headers={"Authorization": f"Bearer {mock_student_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "buildings" in data

    def test_按类型筛选(self, mock_student_token):
        """MAP-S3: 按类型筛选"""
        resp = client.get(
            "/map/buildings?type=食堂",
            headers={"Authorization": f"Bearer {mock_student_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        for b in data["buildings"]:
            assert b["type"] == "食堂"


class TestMapAuth:

    def test_无token返回401(self):
        """地图接口必须认证"""
        resp = client.get("/map/nearby?lat=39.9&lng=116.4")
        assert resp.status_code == 401
