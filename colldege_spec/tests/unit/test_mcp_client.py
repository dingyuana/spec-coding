"""单元测试 — MCP 客户端（MCP-S1~S5）"""
import pytest
from src.core.mcp.client import McpClient


class TestMcpClient:

    def test_connect_returns_client(self, monkeypatch):
        """MCP-S1: MCP 客户端连接成功"""
        client = McpClient()
        result = client.connect()
        assert result is True
        assert client.is_connected is True

    def test_disconnect(self, monkeypatch):
        """MCP-S1: 断开连接"""
        client = McpClient()
        client.connect()
        client.disconnect()
        assert client.is_connected is False

    def test_search_nearby_returns_list(self, monkeypatch):
        """MCP-S3: 搜索附近 POI"""
        client = McpClient()
        client.connect()
        result = client.search_nearby(39.9, 116.4, radius=1000)
        assert isinstance(result, list)
        for item in result:
            assert "name" in item
            assert "lat" in item
            assert "lng" in item

    def test_calc_route_returns_dict(self, monkeypatch):
        """MCP-S4: 计算路线"""
        client = McpClient()
        client.connect()
        result = client.calc_route(39.9, 116.4, 39.91, 116.41)
        assert isinstance(result, dict)
        assert "path" in result
        assert "distance" in result
        assert "walking_time" in result
        assert "steps" in result

    def test_get_building_list(self, monkeypatch):
        """MCP-S3: 获取建筑列表"""
        client = McpClient()
        client.connect()
        result = client.get_building_list(type="食堂")
        assert isinstance(result, list)
        for item in result:
            assert "name" in item
            assert "type" in item

    def test_connect_fail_returns_false(self, monkeypatch):
        """MCP-S2: 连接失败返回 False，不抛异常"""
        client = McpClient()
        monkeypatch.setattr(client, "_do_connect", lambda: (_ for _ in ()).throw(Exception("fail")))
        result = client.connect()
        assert result is False

    def test_mcp_unavailable_returns_fallback(self, monkeypatch):
        """MCP-S5: MCP 不可用时降级返回静态数据"""
        client = McpClient()
        client._fallback_mode = True
        result = client.search_nearby(39.9, 116.4)
        assert isinstance(result, list)
