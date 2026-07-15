# 用户登录模块 — PLAN

## 迭代规划

### Iter 0 — 工程基础（无代码）

| 任务 | 产出 | 状态 |
|------|------|------|
| SPEC.md | 全局 SPEC（定义所有迭代的范围） | ⬜ |
| PLAN.md | 本文件 | ⬜ |
| AGENT.md | 编码规范 | ⬜ |
| package.json / .env / .gitignore | 脚手架 | ⬜ |

### Iter 1 — 工具函数层（3 个文件）

| 顺序 | 任务 | 说明 |
|------|------|------|
| 1.1 | SPEC: 工具函数 | 定义 errors / password / jwt 接口 |
| 1.2 | 测试: `tests/unit/errors.test.js` | TDD RED |
| 1.3 | 代码: `src/utils/errors.js` | GREEN |
| 1.4 | 测试: `tests/unit/password.test.js` | TDD RED |
| 1.5 | 代码: `src/utils/password.js` | GREEN |
| 1.6 | 测试: `tests/unit/jwt.test.js` | TDD RED |
| 1.7 | 代码: `src/utils/jwt.js` | GREEN |

### Iter 2 — 数据模型 + 配置（3 个文件）

| 顺序 | 任务 | 说明 |
|------|------|------|
| 2.1 | SPEC: 数据模型 | 定义 User 模型 + 种子数据 |
| 2.2 | 代码: `src/config/index.js` | 配置（无测试，纯读取环境变量） |
| 2.3 | 测试: `tests/unit/userModel.test.js` | TDD RED |
| 2.4 | 代码: `src/models/user.js` | GREEN |
| 2.5 | 代码: `scripts/seed.js` | 种子数据脚本 |
| 2.6 | 验证: `node scripts/seed.js` | 种子可独立运行 |

### Iter 3 — 服务层（1 个文件）

| 顺序 | 任务 | 说明 |
|------|------|------|
| 3.1 | SPEC: 服务层 | 定义 login 业务逻辑 |
| 3.2 | 测试: `tests/unit/authService.test.js` | TDD RED（mock model/password/jwt） |
| 3.3 | 代码: `src/services/authService.js` | GREEN |

### Iter 4 — 控制层 + 路由 + 应用（4 个文件）

| 顺序 | 任务 | 说明 |
|------|------|------|
| 4.1 | SPEC: HTTP 接口 | 定义路由 / 控制器 / 错误处理 |
| 4.2 | 代码: `src/middleware/errorHandler.js` | 全局异常处理 |
| 4.3 | 代码: `src/controllers/authController.js` | 参数校验 + 格式化 |
| 4.4 | 代码: `src/routes/auth.js` | 路由映射 |
| 4.5 | 代码: `src/app.js`, `src/index.js` | 应用组装 + 入口 |
| 4.6 | 测试: `tests/integration/auth.test.js` | TDD RED → GREEN |

### Iter 5 — 完整验证

| 任务 | 说明 |
|------|------|
| `npm install` | 安装依赖 |
| `npm test` | 全部 25 条测试通过 ✅ |
| 手动 curl 验证 | 4 个 Scenario 手动复现 |

## 依赖链

```
Iter 0（工程基础）
  ↓
Iter 1（工具函数）→ 独立，无项目内依赖
  ↓
Iter 2（模型 + 配置）→ 依赖 Iter 1 的 errors/password
  ↓
Iter 3（服务层）→ 依赖 Iter 1+2
  ↓
Iter 4（控制层）→ 依赖 Iter 3
  ↓
Iter 5（验证）→ 依赖全部
```

## 里程碑

| M1 | 工具函数全绿 | Iter 1 完成 |
| M2 | 用户模型 + 种子可用 | Iter 2 完成 |
| M3 | 登录业务逻辑测试通过 | Iter 3 完成 |
| M4 | HTTP 接口全部覆盖 | Iter 4 完成 |
| M5 | 25 条测试全部通过 | ✅ 全部完成 |