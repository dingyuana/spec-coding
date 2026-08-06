# Iter 5：地图模块——高德 MCP 接入 + 优雅降级

> **场景带入 → 发现问题 → 方案迭代 → 原理拆解 → 效果对比 → 情绪升华**

---

## 一、场景带入：校门口迷路的新生

大一新生小王拖着行李箱站在校门口，导航显示"到达"，但他看着眼前的停车场，完全不知道该往哪走。

他需要一个功能：**从校门到宿舍楼的完整步行路线**——每一步往哪转、走多远、几分钟。

这就要接入高德地图 API。

![](imgs/09/01-map-route.svg)

## 二、什么是 MCP

MCP（Model Context Protocol）是一个**标准化的服务调用协议**——

不是直接调高德 HTTP API，而是通过 MCP 客户端封装：

```
请求 → MCP Client → 高德服务 → 返回结构化数据
          ↑
     重试 / 降级 / 超时
```

**好处：**
1. 更换地图服务商只需换 MCP 客户端（接口不变）
2. 服务不可用时有降级方案（mock 数据）
3. 统一的超时和重试机制

## 三、MCP 客户端封装

```python
# src/core/mcp/client.py
class McpClient:
    def __init__(self):
        self.is_connected = False

    def connect(self) -> bool:
        try:
            self._do_connect()
            self.is_connected = True
            return True
        except Exception:
            logger.warning("MCP 连接失败，使用降级数据")
            return False

    def search_nearby(self, lat, lng, types) -> list:
        if not self.is_connected:
            return self._fallback_nearby(lat, lng, types)
        return self._do_search(lat, lng, types)

    def calc_route(self, slat, slng, dlat, dlng, sname, dname) -> dict:
        if not self.is_connected:
            return self._fallback_route(slat, slng, dlat, dlng, sname, dname)
        return self._do_calc(slat, slng, dlat, dlng, sname, dname)
```

## 四、三个接口

| 接口 | 功能 |
|------|------|
| `get_nearby_buildings(lat, lng)` | 附近建筑：宿舍楼、食堂、教学楼、图书馆 |
| `calc_route(slat, slng, dlat, dlng, sname, dname)` | 完整路线：path + steps + 步行时间 |
| `get_building_list(type?)` | 校园建筑列表，可按类型筛选 |

![](imgs/09/02-mcp-architecture.svg)

## 五、路线返回数据结构

```json
{
  "total_distance": 800,
  "walking_time": 12,
  "path": [[116.40, 39.90], [116.405, 39.902], [116.41, 39.905]],
  "steps": [
    "从校门出发，沿主路向南步行 200 米",
    "左转进入学生活动中心前的道路",
    "直行 300 米到达 A1 栋宿舍楼"
  ]
}
```

**路径坐标点给地图组件画图，中文步骤给新用户看。**

## 六、优雅降级测试

```python
# tests/unit/test_map_service.py
def test_mcp_unavailable_returns_fallback(self, monkeypatch):
    mcp = McpClient()
    mcp.connect()   # mock 返回 False
    result = get_nearby_buildings(39.9, 116.4)
    assert len(result) > 0   # 降级数据也要有内容
```

**MCP 连不上 ≠ 功能不可用**——降级数据保证系统始终可用。

## 七、情绪升华

校园导航不只是"两点之间的直线距离"——
它是**一个迷路新生从校门到宿舍的完整指引**。

每一步、每一个转弯、每一栋建筑——都是代码写给用户的关怀。

**好的系统不仅功能全，还懂得在出问题的时候给自己留条退路。**
