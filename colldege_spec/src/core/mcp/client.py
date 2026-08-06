from __future__ import annotations

from typing import Any


class McpClient:
    """MCP 客户端 — 高德地图服务适配器（mock 模式）"""

    def __init__(self):
        self.is_connected = False
        self._fallback_mode = False

    def connect(self) -> bool:
        try:
            self._do_connect()
            self.is_connected = True
            return True
        except Exception:
            self.is_connected = False
            return False

    def disconnect(self) -> None:
        self.is_connected = False

    def _do_connect(self) -> None:
        pass

    def search_nearby(self, lat: float, lng: float, radius: int = 1000) -> list[dict[str, Any]]:
        if self._fallback_mode:
            return self._fallback_nearby(lat, lng)
        return [
            {"name": "食堂A", "lat": lat + 0.001, "lng": lng + 0.001, "distance": 80},
            {"name": "图书馆", "lat": lat + 0.002, "lng": lng + 0.002, "distance": 150},
            {"name": "教学楼", "lat": lat + 0.0005, "lng": lng + 0.0005, "distance": 40},
        ]

    def calc_route(self, from_lat: float, from_lng: float, to_lat: float, to_lng: float) -> dict[str, Any]:
        return {
            "path": [
                {"lat": from_lat, "lng": from_lng},
                {"lat": (from_lat + to_lat) / 2, "lng": (from_lng + to_lng) / 2},
                {"lat": to_lat, "lng": to_lng},
            ],
            "distance": 500,
            "walking_time": 600,
            "steps": [
                {"instruction": "从起点向东直行 200 米", "distance": 200},
                {"instruction": "左转进入校园主干道", "distance": 150},
                {"instruction": "到达目的地", "distance": 150},
            ],
        }

    def get_building_list(self, type: str = None) -> list[dict[str, str]]:
        buildings = [
            {"name": "食堂A", "type": "食堂", "lat": 39.904, "lng": 116.407},
            {"name": "图书馆", "type": "图书馆", "lat": 39.905, "lng": 116.408},
            {"name": "教学楼", "type": "教学楼", "lat": 39.906, "lng": 116.409},
            {"name": "体育馆", "type": "体育馆", "lat": 39.903, "lng": 116.406},
            {"name": "宿舍A栋", "type": "宿舍", "lat": 39.902, "lng": 116.405},
            {"name": "校门", "type": "校门", "lat": 39.900, "lng": 116.400},
        ]
        if type:
            return [b for b in buildings if b["type"] == type]
        return buildings

    def _fallback_nearby(self, lat: float, lng: float) -> list[dict[str, Any]]:
        return [
            {"name": "[兜底] 食堂", "lat": lat + 0.001, "lng": lng + 0.001, "distance": 100},
        ]
