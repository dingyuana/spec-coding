"""单元测试 — MapService（MAP-S1~S4）"""
import pytest
from src.services.map_service import get_nearby_buildings, calc_route, get_building_list


class TestMapService:

    def test_get_nearby_返回建筑列表(self):
        """MAP-S1: 返回附近建筑（名称/坐标/距离）"""
        result = get_nearby_buildings(lat=39.9, lng=116.4, radius=1000)
        assert isinstance(result, list)
        if result:
            assert "name" in result[0]
            assert "lat" in result[0]
            assert "lng" in result[0]
            assert "distance" in result[0]

    def test_calc_route_返回完整路线(self):
        """MAP-S2: 返回路径/距离/步行时间/步骤"""
        result = calc_route(39.9, 116.4, 39.91, 116.41)
        assert "path" in result
        assert "distance" in result
        assert "walking_time" in result
        assert "steps" in result
        assert isinstance(result["path"], list)
        assert isinstance(result["steps"], list)

    def test_calc_route_起点终点为中文(self):
        """MAP-S4: 起点终点为校园建筑名"""
        result = calc_route(39.9, 116.4, 39.91, 116.41,
                            from_name="校门", to_name="食堂")
        assert result["from"]["name"] == "校门"
        assert result["to"]["name"] == "食堂"

    def test_get_building_list_按类型筛选(self):
        """MAP-S3: 按类型筛选建筑"""
        result = get_building_list(type="食堂")
        assert isinstance(result, list)
        for item in result:
            assert item["type"] == "食堂"

    def test_get_building_list_全类型(self):
        """MAP-S3: 不传 type 返回所有建筑"""
        result = get_building_list()
        assert isinstance(result, list)

    def test_mcp_unavailable_returns_fallback(self):
        """MCP-S5: MCP 不可用时返回兜底数据"""
        result = get_nearby_buildings(lat=39.9, lng=116.4, force_fallback=True)
        assert isinstance(result, list)
