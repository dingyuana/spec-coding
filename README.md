# Spec Coding — 用户登录模块实战教程

> **从"会写代码"到"会设计代码"——SDD + TDD 完整流程实战**

---

## 项目简介

这是一个面向初学者的 **SDD（Spec-Driven Development）+ TDD（Test-Driven Development）** 实战教程项目。通过实现一个**用户登录模块**，完整演示从"写契约"到"测试通过"的全过程。

### 你将会学到

- 如何用 **SPEC.md** 把需求写成契约
- 如何用 **PLAN.md** 把任务排成迭代
- 如何用 **AGENT.md** 把规范写成门禁
- 如何用 **TDD** 先写测试再写代码
- 如何用 **6 个迭代**逐步交付一个完整功能

---

## 项目结构

```
user-login/
├── SPEC.md              # 业务契约（5 个迭代的范围定义）
├── PLAN.md              # 迭代规划（Iter 0-5）
├── AGENT.md             # 编码规范（禁止项 + 分层规则）
├── package.json         # 依赖与脚本
├── .env.example         # 环境变量模板
├── .gitignore           # 忽略规则
│
├── src/                 # 源码（12 个文件）
│   ├── config/          # 配置
│   ├── utils/           # 工具函数（errors / password / jwt）
│   ├── models/          # 数据模型（User）
│   ├── services/        # 服务层（authService）
│   ├── controllers/     # 控制器
│   ├── routes/          # 路由
│   └── middleware/      # 错误处理
│
├── scripts/
│   └── seed.js          # 种子数据（预置 admin 用户）
│
├── tests/               # 30 条测试
│   ├── unit/            # 单元测试（5 个文件）
│   └── integration/     # 集成测试（1 个文件）
│
└── tutorials/           # 10 篇教程 + 20 张配图
    ├── imgs/            # 科技蓝风格 SVG 配图
    ├── 00-sdd-tdd-intro.md
    ├── 01-spec-tutorial.md
    ├── 02-plan-tutorial.md
    ├── 03-agent-tutorial.md
    ├── 04-scaffold-tutorial.md
    ├── 05-iter1-tutorial.md
    ├── 06-iter2-tutorial.md
    ├── 07-iter3-tutorial.md
    ├── 08-iter4-tutorial.md
    └── 09-iter5-tutorial.md
```

---

## 快速开始

```bash
# 1. 克隆项目
git clone git@github.com:dingyuana/spec-coding.git
cd spec-coding

# 2. 配置环境变量
cp .env.example .env

# 3. 安装依赖
npm install

# 4. 运行测试（验证环境就绪）
npm test
```

预期输出：

```
Test Suites: 6 passed, 6 total
Tests:       30 passed, 30 total
```

---

## 6 个迭代路径

| 迭代 | 内容 | 文件数 | 测试数 |
|------|------|--------|--------|
| Iter 0 | SPEC / PLAN / AGENT / 脚手架 | 6 | 0 |
| Iter 1 | 工具函数（errors + password + jwt） | 3 | 13 ✅ |
| Iter 2 | 数据模型 + 种子数据 | 2 | 5 ✅ |
| Iter 3 | 服务层（login 业务逻辑） | 1 | 3 ✅ |
| Iter 4 | HTTP 接口（controller + route + middleware） | 5 | 8 ✅ |
| Iter 5 | 完整验证 | — | 30 ✅ |

---

## 技术栈

| 技术 | 用途 |
|------|------|
| Node.js 18+ | 运行环境 |
| Koa 2 | Web 框架 |
| bcryptjs | 密码加密（10 rounds） |
| jsonwebtoken | JWT 令牌（24h 过期） |
| Jest | 测试框架 |
| Supertest | HTTP 集成测试 |
| dotenv | 环境变量管理 |

---

## 教程索引

| # | 文章 | 核心内容 |
|---|------|---------|
| [00](tutorials/00-sdd-tdd-intro.md) | SDD+TDD 框架总览 | 迭代规划 + 方法论 |
| [01](tutorials/01-spec-tutorial.md) | 把需求写成契约 | SPEC.md 实战 |
| [02](tutorials/02-plan-tutorial.md) | 把任务排成地图 | PLAN.md 实战 |
| [03](tutorials/03-agent-tutorial.md) | 把规范写成门禁 | AGENT.md 实战 |
| [04](tutorials/04-scaffold-tutorial.md) | 搭好工程底座 | package.json / .env / .gitignore |
| [05](tutorials/05-iter1-tutorial.md) | Iter 1：工具函数层 | RED→GREEN 完整循环 |
| [06](tutorials/06-iter2-tutorial.md) | Iter 2：数据模型 + 种子 | 幂等性 seed |
| [07](tutorials/07-iter3-tutorial.md) | Iter 3：服务层 | Mock 隔离测试 |
| [08](tutorials/08-iter4-tutorial.md) | Iter 4：HTTP 接口层 | 4 个 Scenario 集成测试 |
| [09](tutorials/09-iter5-tutorial.md) | 完整验证 + 回顾 | 30 条测试全部通过 |

---

## 验证

```bash
$ npm test

PASS tests/unit/errors.test.js          (6 条)
PASS tests/unit/password.test.js        (4 条)
PASS tests/unit/jwt.test.js             (3 条)
PASS tests/unit/userModel.test.js       (5 条)
PASS tests/unit/authService.test.js     (3 条)
PASS tests/integration/auth.test.js     (8 条)

Test Suites: 6 passed, 6 total
Tests:       30 passed, 30 total
```

## License

MIT