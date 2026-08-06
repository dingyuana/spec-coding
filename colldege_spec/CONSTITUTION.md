# CONSTITUTION — 大学新生报到系统

> 定义 CEO/Hermes/OpenCode 三角色及禁止行为

---

## 一、三角色定义

| 角色 | 身份 | 职责 | 禁止 |
|------|------|------|------|
| CEO | 用户 | 提出需求、参与评审、做出最终业务决策 | 直接生成代码 |
| Hermes | AI 助手 | 产品经理 + 规范制定者，编写 SPEC/AGENT/PLAN，调度执行，组织评审，验收代码 | 在无 SPEC 时指令编码 |
| OpenCode | 执行引擎 | 按 skill.yaml 和 specs/*.yaml 生成代码/测试/Git 操作 | 猜测业务逻辑，推送 main/develop |

---

## 二、项目基本信息

| 项目 | 内容 |
|------|------|
| 名称 | colldege_spec |
| 一句话 | 大学新生报到系统 — 微信学生端 + Web 辅导员/管理员端 + 高德 MCP 地图导航 |
| 后端 | Python 3.11 + FastAPI + SQLAlchemy + SQLite |
| 学生端 | 微信小程序（原生 WXML） |
| 管理端 | Vue 3 + Element Plus |
| 地图 | 高德地图，MCP 协议连接 |
| 角色 | 学生 / 辅导员 / 管理员（三层） |
| 认证 | JWT + 微信 code 换 session_key |
| 测试 | pytest + httpx + pytest-cov（覆盖率 ≥ 80%） |
| 质量 | ruff + mypy + pre-commit + GitHub Actions |

---

## 三、工作流闭环

```
立法：Hermes 建立规范文件（README→SPEC→AGENT→PLAN→specs/*.yaml）
   ↓
执行：OpenCode 按规范编码（skill 驱动，TDD：RED→GREEN）
   ↓
司法：Hermes 验收代码（对照 SPEC 验收，测试全绿）
   ↓
归档：更新 PLAN.md 状态，Git commit + push develop
```

---

## 四、禁止行为

| 禁止项 | 原因 |
|--------|------|
| 硬编码密码/密钥/微信 AppID | 安全风险，必须从 .env 读取 |
| 在 API 响应中返回密码哈希 | 信息泄露 |
| `except Exception: pass` | 吞异常，无法定位问题 |
| 打印敏感信息（openid、session_key）到日志 | 信息泄露 |
| MCP 连接硬编码 endpoint | 配置应可替换 |
| routes 直接操作数据库 | 分层架构破坏 |
| service 返回 HTTP 响应 | 职责分离 |
| 跳过 TDD 循环（先写代码后写测试） | 教学质量受损 |
| 提交 .env 或数据库文件 | 密钥泄露 |
| 未经评审直接修改 SPEC | 契约变更需走评审 |

---

## 五、分支策略

- `develop` — 开发分支（日常开发）
- `main` — 发布分支（仅合并已完成迭代）
- 禁止直接向 main 推送

---

## 六、Git 提交规范

格式：`type: 简短描述（≤50字）`

| type | 含义 |
|------|------|
| feat | 新功能 |
| fix | 缺陷修复 |
| docs | 文档变更 |
| refactor | 重构 |
| perf | 性能优化 |
| test | 测试 |
| chore | 工具/配置 |

---

## 七、模块职责边界

| 模块 | 职责 | 依赖 |
|------|------|------|
| auth | 三端认证（微信学生 / 管理员 / 辅导员） | 无 |
| student | 学生报到信息管理（含扩展字段） | auth |
| counselor | 辅导员端（本班查看/审核/看板） | auth, student |
| admin | 管理端全局（审核/导出/看板/日志/辅导员管理） | auth, student, counselor |
| map | 高德 MCP 地图导航 | auth, mcp |
| mcp | MCP 客户端封装（高德地图协议） | 无 |

**权限边界（重要）：**
- 辅导员只能操作 **class_name 匹配本班**的学生数据
- 管理员可操作**全局**所有学生数据
- 学生只能查看/修改**自己**的报到信息

**禁止跨模块直接调用**：例如 admin 模块禁止直接 import student 模块的 service，应通过 router 层调用。

---

## 八、质量门禁

| 门禁 | 工具 | 阈值 |
|------|------|------|
| 代码风格 | ruff | 0 errors |
| 类型检查 | mypy | strict mode, 0 errors |
| 单元测试 | pytest | 覆盖率 ≥ 80% |
| CI 流水线 | GitHub Actions | 全部阶段通过 |
| OpenSpec 校验 | yaml 语法 | 纯 YAML，无 markdown |

---

## 九、迭代管理

每个迭代遵循 TDD 流程：

```
① 读 SPEC 确定本迭代范围
   ↓
② 写测试（RED）— 先跑，确认失败
   ↓
③ 写代码（GREEN）— 仅满足测试
   ↓
④ 跑测试，确认全绿
   ↓
⑤ 更新 PLAN.md 状态
   ↓
⑥ Git commit + push
```

WIP 限制：实现阶段同时只处理 1 个迭代。
