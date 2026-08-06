# 技术方案 — 大学新生报到系统

> 本文件记录项目的技术方案设计，包括架构设计、技术选型、接口设计、数据模型、部署方案。

---

## 一、系统架构

### 1.1 整体架构图

```
┌──────────────────────────────────────────────────────────┐
│                    前端层                                  │
│  ┌─────────────────────┐   ┌─────────────────────────┐  │
│  │   微信小程序          │   │    Web 管理端             │  │
│  │   (学生端)           │   │    (Vue 3 + Element Plus)│  │
│  │  - 微信授权登录       │   │  - 管理员登录              │  │
│  │  - 报到信息填写       │   │  - 审核 + 导出 + 看板     │  │
│  │  - 校园地图导航       │   │                           │  │
│  └────────┬────────────┘   └──────────┬────────────────┘  │
└───────────┼────────────────────────────┼─────────────────┘
            │                            │
            ▼                            ▼
┌──────────────────────────────────────────────────────────┐
│                    API 网关层                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │               FastAPI (Python 3.11)                   │ │
│  │  - JWT 认证中间件                                     │ │
│  │  - 统一异常处理                                       │ │
│  │  - OpenAPI 文档（/docs）                              │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────────────────────┐
│                    服务层                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ AuthService│Registration│  AdminSvc  │ MapService│   │
│  │          │    Service   │           │          │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└──────────────────────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────────────────────┐
│                    数据层                                  │
│  ┌─────────────────┐        ┌──────────────────────┐   │
│  │ SQLAlchemy 2.0  │        │ MCP 客户端            │   │
│  │ (async SQLite)  │        │ (Model Context Proto) │   │
│  └─────────────────┘        └──────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### 1.2 分层说明

| 层 | 职责 | 技术 |
|----|------|------|
| 前端层 | 用户交互 | 微信小程序 / Vue 3 |
| API 网关层 | 路由 + 认证 + 异常 | FastAPI |
| 服务层 | 业务逻辑 | Python async |
| 数据层 | 持久化 + 外部服务 | SQLAlchemy / MCP |

---

## 二、技术选型

### 2.1 后端技术栈

| 组件 | 选择 | 理由 |
|------|------|------|
| Web 框架 | FastAPI | 异步、自动 OpenAPI 文档、类型校验 |
| 数据库 ORM | SQLAlchemy 2.0 | 类型安全、async 支持 |
| 数据库 | SQLite | 教学简化，零部署成本 |
| 认证 | JWT (python-jose) | 无状态、跨端通用 |
| 密码加密 | passlib[bcrypt] | 行业标准 |
| 配置管理 | python-dotenv | 环境变量注入 |
| 测试 | pytest + httpx | 异步测试支持 |
| 代码质量 | ruff + mypy | 风格 + 类型检查 |

### 2.2 前端技术栈

| 端 | 技术 | 理由 |
|----|------|------|
| 微信小程序 | 原生 WXML + WXSS | 微信官方推荐 |
| Web 管理端 | Vue 3 + Element Plus | 组件丰富，上手快 |
| HTTP 客户端 | 小程序 wx.request / axios | 平台原生 / 生态成熟 |

### 2.3 地图技术栈

| 组件 | 选择 | 理由 |
|------|------|------|
| 协议 | MCP (Model Context Protocol) | 模块化、可扩展 |
| 地图数据 | mock（教学阶段） | 无需依赖外部服务 |
| 降级策略 | 静态兜底数据 + 日志警告 | 服务不可用不崩溃 |

---

## 三、接口设计

### 3.1 认证接口

```
POST /auth/student
Content-Type: application/json
{
  "code": "0a1XXXXX01XXXXXX"  // 微信 wx.login 返回
}
→ 200: { "token": "eyJ...", "expires_in": 86400 }

POST /auth/admin
Content-Type: application/json
{
  "username": "admin",
  "password": "admin123"
}
→ 200: { "token": "eyJ...", "expires_in": 86400 }
```

### 3.2 报到信息接口（学生端）

```
POST /student/registration
Authorization: Bearer {token}
Content-Type: application/json
{
  "name": "张三",
  "student_id": "20260001",
  "college": "计算机学院",
  "building": "A1栋",
  "phone": "13800138000"
}
→ 201: { "id": 1, "status": "SUBMITTED" }
→ 409: { "detail": "已存在报到记录" }
→ 422: { "detail": "字段校验失败" }

GET /student/registration
Authorization: Bearer {token}
→ 200: { "id": 1, "status": "SUBMITTED", ... }
→ 404: { "detail": "未找到报到记录" }

PUT /student/registration
Authorization: Bearer {token}
Content-Type: application/json
{ "name": "张三", ... }
→ 200: { "id": 1, "status": "SUBMITTED", ... }
→ 403: { "detail": "仅 REJECTED 状态允许修改" }
```

### 3.3 管理端接口

```
GET /admin/students?page=1&size=20&status=SUBMITTED&college=计算机学院
Authorization: Bearer {token}
→ 200: { "items": [...], "total": 120, "page": 1, "size": 20 }

POST /admin/audit/{student_id}
Authorization: Bearer {token}
Content-Type: application/json
{ "action": "APPROVED" }
或
{ "action": "REJECTED", "reason": "学号格式错误" }
→ 200: { "id": 1, "status": "APPROVED" }

GET /admin/export
Authorization: Bearer {token}
→ 200: (CSV 文件流)

GET /admin/dashboard
Authorization: Bearer {token}
→ 200: {
    "today_count": 120,
    "total_count": 500,
    "by_status": { "SUBMITTED": 80, "APPROVED": 40, "REJECTED": 5 },
    "by_college": { "计算机学院": 80, "经济学院": 60, ... }
  }
```

### 3.4 地图接口

```
GET /map/nearby?lat=39.9&lng=116.4&radius=1000
Authorization: Bearer {token}
→ 200: {
    "buildings": [
      { "name": "食堂", "lat": 39.91, "lng": 116.41, "distance": 500 },
      { "name": "图书馆", "lat": 39.92, "lng": 116.42, "distance": 800 }
    ]
  }

GET /map/route?from_lat=39.9&from_lng=116.4&to_lat=39.91&to_lng=116.41
Authorization: Bearer {token}
→ 200: {
    "path": [
      { "lat": 39.9, "lng": 116.4 },
      { "lat": 39.905, "lng": 116.405 },
      { "lat": 39.91, "lng": 116.41 }
    ],
    "distance": 500,
    "walking_time": 6
  }
```

---

## 四、数据模型设计

### 4.1 Student 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, auto | 主键 |
| openid | String(64) | not null, unique | 微信 openid |
| student_id | String(20) | not null, unique | 学号 |
| name | String(50) | not null | 姓名 |
| college | String(100) | not null | 学院 |
| building | String(50) | not null | 宿舍楼栋 |
| phone | String(20) | not null | 联系方式 |
| status | Enum | not null, default=PENDING | 状态 |
| reject_reason | Text | nullable | 驳回原因 |
| created_at | DateTime | not null | 创建时间 |
| updated_at | DateTime | not null | 更新时间 |

### 4.2 Admin 表（预置）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, auto | 主键 |
| username | String(50) | not null, unique | 用户名 |
| password_hash | String(128) | not null | bcrypt 哈希 |
| role | String(20) | not null | 角色（admin） |
| created_at | DateTime | not null | 创建时间 |

### 4.3 Status 枚举

```python
class Status(str, Enum):
    PENDING = "PENDING"      # 待提交
    SUBMITTED = "SUBMITTED"  # 已提交
    APPROVED = "APPROVED"    # 审核通过
    REJECTED = "REJECTED"    # 审核驳回
```

---

## 五、MCP 集成方案

### 5.1 MCP 架构

```
FastAPI 应用
    │
    ▼
┌──────────────────┐
│ mcp_client.py    │  ← MCP 客户端封装
│ - connect()      │    连接外部地图服务
│ - call()         │    调用地图工具
│ - disconnect()   │    断开连接
└──────────────────┘
    │
    ▼
┌──────────────────┐
│ 外部地图服务       │  ← 通过 MCP 协议提供
│ - 建筑查询        │    地图能力
│ - 路径规划        │
└──────────────────┘
```

### 5.2 MCP 配置

从 `.env` 读取：

```
MCP_ENABLED=false          # 是否启用真实 MCP
MCP_TRANSPORT=stdio        # 传输方式
MCP_COMMAND=npx            # 启动命令
MCP_ARGS=maps-service      # 服务标识
MCP_TIMEOUT=30             # 超时秒数
```

### 5.3 降级策略

```
MCP_ENABLED=false 或 MCP 连接失败
    ↓
使用内置静态地图数据
    ↓
日志记录：WARNING "MCP 不可用，使用兜底数据"
    ↓
正常返回（不报错）
```

---

## 六、部署方案

### 6.1 开发环境

```bash
# 本地开发
pip install -r requirements-dev.txt
uvicorn src.main:app --reload --port 8000
```

### 6.2 生产环境

| 组件 | 方案 |
|------|------|
| 应用服务器 | Gunicorn + uvicorn workers |
| 数据库 | PostgreSQL（生产迁移） |
| 反向代理 | Nginx |
| 微信接口 | 配置正式 AppID/Secret |
| MCP | 部署 MCP 地图服务 |
| 前端 | 微信小程序提交审核 / Vue 打包部署 |

### 6.3 CI 流水线

```yaml
# .github/workflows/ci.yml
stages:
  - lint      (ruff check)
  - type      (mypy strict)
  - test      (pytest --cov)
  - security  (pip-audit)
```

---

## 七、性能指标

| 指标 | 目标值 |
|------|--------|
| API P50 延迟 | < 100ms |
| API P99 延迟 | < 300ms |
| 测试覆盖率 | ≥ 80% |
| 并发支持 | 500 人同时在线（教学规模） |

---

## 八、风险与应对

| 风险 | 影响 | 应对 |
|------|------|------|
| MCP 服务不可用 | 地图功能失效 | 静态兜底数据 + 日志告警 |
| 微信接口限流 | 登录失败 | 本地缓存 session_key，减少调用频率 |
| SQLite 并发瓶颈 | 大量并发写入慢 | 生产迁移 PostgreSQL |
| 学号格式不规范 | 数据不一致 | Pydantic 校验 + 正则 |

---

## 九、文档版本

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-08-06 | 初始技术方案 |
