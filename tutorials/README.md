# SDD+TDD 实战系列：用户登录模块

## 系列文章（10 篇）

| # | 文章 | 核心产物 |
|---|------|---------|
| 00 | [SDD+TDD 框架总览](00-sdd-tdd-intro.md) | 方法论 |
| 01 | [把需求写成契约](01-spec-tutorial.md) | `SPEC.md` |
| 02 | [把任务排成地图](02-plan-tutorial.md) | `PLAN.md` |
| 03 | [把规范写成门禁](03-agent-tutorial.md) | `AGENT.md` |
| 04 | [搭好工程底座](04-scaffold-tutorial.md) | `package.json` `.env` `.gitignore` |
| 05 | [Iter 1：工具函数层](05-iter1-tutorial.md) | `utils/errors.js` `utils/password.js` `utils/jwt.js` |
| 06 | [Iter 2：数据模型 + 种子](06-iter2-tutorial.md) | `models/user.js` `scripts/seed.js` |
| 07 | [Iter 3：服务层](07-iter3-tutorial.md) | `services/authService.js` |
| 08 | [Iter 4：HTTP 接口层](08-iter4-tutorial.md) | `controllers/` `routes/` `middleware/` |
| 09 | [完整验证 + 回顾](09-iter5-tutorial.md) | 全部通过 ✅ |

## 迭代流程

```
Iter 0: SPEC / PLAN / AGENT / 脚手架
  ↓
Iter 1: 工具函数 → 3 文件, 13 测试
  ↓
Iter 2: 数据模型 + 种子 → 2 文件, 5 测试
  ↓
Iter 3: 服务层 → 1 文件, 3 测试
  ↓
Iter 4: HTTP 接口 → 5 文件, 8 测试
  ↓
Iter 5: 验证 → 30 测试全部通过
```

## 验证

```bash
$ npm test
Test Suites: 6 passed, 6 total
Tests:       30 passed, 30 total
```