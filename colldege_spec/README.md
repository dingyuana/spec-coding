# 大学新生报到系统

> 面向大学新生报到场景的双端系统：微信学生端 + Web 管理端 + MCP 校园地图导航

---

## 一句话描述

让大学新生通过微信小程序完成报到登记，管理员通过 Web 端面审核信息并查看数据看板，校园地图通过 MCP 协议提供导航能力。

---

## 技术栈

| 层 | 技术 | 说明 |
|----|------|------|
| 后端 | Python 3.11 + FastAPI | 异步框架，RESTful API |
| 数据库 | SQLite + SQLAlchemy 2.0 | 教学简化，async 模式 |
| 认证 | JWT + 微信 code | 双端登录（学生微信/管理员密码） |
| 学生端 | 微信小程序（原生 WXML） | 微信授权 + 报到填写 + 地图导航 |
| 管理端 | Vue 3 + Element Plus | 审核列表 + 导出 CSV + 看板 |
| 地图 | MCP (Model Context Protocol) | 连接外部地图服务 |
| 测试 | pytest + httpx + pytest-cov | 覆盖率 ≥ 80% |
| 质量 | ruff + mypy + pre-commit | CI 流水线 |

---

## 快速启动

```bash
# 1. 配置环境变量
cp .env.example .env

# 2. 安装依赖
pip install -r requirements-dev.txt

# 3. 初始化数据库
python scripts/init_db.py

# 4. 运行测试
pytest -v --cov --cov-fail-under=80

# 5. 启动开发服务器
uvicorn src.main:app --reload --port 8000
```

---

## 目录结构

```
colldege_spec/
├── CONSTITUTION.md          # 三角色定义 + 禁止行为
├── AGENT.md                 # FastAPI 编码规范
├── PLAN.md                  # 迭代规划（Iter 0-6）
├── SPEC.md                  # 全局业务契约
├── README.md                # 本文件
├── goals.yaml               # 项目目标 + KPI
├── kanban.yaml              # 看板 + WIP 限制
│
├── docs/
│   ├── REQUIREMENTS.md      # 需求分析书
│   └── TECHNICAL_DESIGN.md  # 技术方案
│
├── specs/
│   ├── _template.yaml       # OpenSpec 模板
│   ├── auth.yaml            # 认证模块契约
│   ├── student.yaml         # 学生报到模块契约
│   ├── admin.yaml           # 管理端模块契约
│   ├── map.yaml             # 地图模块契约
│   └── mcp.yaml             # MCP 客户端契约
│
├── src/
│   ├── main.py              # FastAPI 入口
│   ├── config/              # 配置管理
│   ├── core/                # 核心模块（auth / mcp）
│   ├── routers/             # 路由层
│   ├── services/            # 业务逻辑层
│   ├── models/              # SQLAlchemy 模型
│   ├── schemas/             # Pydantic 数据模型
│   └── utils/               # 工具函数
│
├── scripts/
│   ├── init_db.py           # 初始化数据库
│   └── seed.py              # 预置管理员
│
├── tests/
│   ├── unit/                # 单元测试
│   └── integration/         # 集成测试
│
├── frontend/
│   ├── miniapp/             # 微信小程序源码
│   └── admin/               # Vue 3 管理端源码
│
└── .github/workflows/
    └── ci.yml               # CI 流水线
```

---

## 文档链接

| 文档 | 路径 |
|------|------|
| 需求分析书 | [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) |
| 技术方案 | [docs/TECHNICAL_DESIGN.md](docs/TECHNICAL_DESIGN.md) |
| 业务契约 | [SPEC.md](SPEC.md) |
| 迭代计划 | [PLAN.md](PLAN.md) |
| 编码规范 | [AGENT.md](AGENT.md) |
| OpenSpec | [specs/](specs/) |

---

## 迭代路线图

```
Iter 0:  工程基础（规范文件 + 脚手架）
Iter 1:  认证模块（双端登录）
Iter 2:  报到信息模块（学生端）
Iter 3:  管理端模块（审核 + 导出 + 看板）
Iter 4:  校园地图模块（MCP 导航）
Iter 5:  集成测试（端到端）
Iter 6:  完整验证 + 回顾
```

---

## License

MIT
