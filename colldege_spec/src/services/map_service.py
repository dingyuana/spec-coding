from __future__ import annotations

import logging
from src.core.mcp.client import McpClient

logger = logging.getLogger("colldege")

_mcp = McpClient()


def get_nearby_buildings(lat: float, lng: float, radius: int = 1000, force_fallback: bool = False) -> list[dict]:
    if force_fallback:
        client = McpClient()
        client._fallback_mode = True
        return client.search_nearby(lat, lng, radius)
    try:
        return _mcp.search_nearby(lat, lng, radius)
    except Exception as e:
        logger.warning(f"MCP 不可用，降级为静态数据: {e}")
        client = McpClient()
        client._fallback_mode = True
        return client.search_nearby(lat, lng, radius)


def calc_route(
    from_lat: float, from_lng: float,
    to_lat: float, to_lng: float,
    from_name: str = None,
    to_name: str = None,
) -> dict:
    route = _mcp.calc_route(from_lat, from_lng, to_lat, to_lng)
    route["from"] = {"name": from_name or "起点", "lat": from_lat, "lng": from_lng}
    route["to"] = {"name": to_name or "终点", "lat": to_lat, "lng": to_lng}
    return route


def get_building_list(type: str = None) -> list[dict]:
    try:
        return _mcp.get_building_list(type)
    except Exception as e:
        logger.warning(f"MCP 不可用，降级为静态数据: {e}")
        client = McpClient()
        client._fallback_mode = True
        return client.get_building_list(type)
