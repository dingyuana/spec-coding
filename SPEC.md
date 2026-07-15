# 用户登录模块 — SPEC（全局契约）

> 本文档定义整个项目的完整契约。每个迭代只实现其中一部分。

---

## 一、Feature

### Scenario 1: 正常登录
- Given 数据库中存在用户 admin
- When 用户提交正确的用户名和密码
- Then 返回 200 和 JWT Token
- And Token payload 包含 user_id

### Scenario 2: 密码错误
- Given 数据库中存在用户 admin
- When 用户提交正确的用户名但错误的密码
- Then 返回 401
- And 响应体为 `{ "error": "用户名或密码错误" }`

### Scenario 3: 用户不存在
- Given 数据库中不存在用户 hacker
- When 用户提交用户名 hacker
- Then 返回 401
- And 响应体为 `{ "error": "用户名或密码错误" }`（与 Scenario 2 一致）

### Scenario 4: 参数缺失
- Given 请求体缺少 username 或 password
- When 用户提交不完整的登录请求
- Then 返回 400
- And 响应体为 `{ "error": "用户名和密码不能为空" }`

---

## 二、各迭代 SPEC

### Iter 1 — 工具函数接口

**errors.js:**
- `AppError(message, statusCode)` — 自定义错误类
- `Errors.INVALID_CREDENTIALS` — 401 错误
- `Errors.MISSING_PARAMS(msg)` — 400 错误工厂
- `Errors.INTERNAL` — 500 错误

**password.js:**
- `hashPassword(plain)` → 返回 bcrypt 哈希
- `verifyPassword(plain, hash)` → 返回 boolean

**jwt.js:**
- `signToken(userId)` → 返回 JWT 字符串，payload 含 `{ user_id, exp }`
- `verifyToken(token)` → 返回 decoded payload

### Iter 2 — 数据模型 + 配置

**config/index.js:**
- 从 .env 读取: PORT, JWT_SECRET, JWT_EXPIRES_IN, BCRYPT_ROUNDS
- 默认 JWT_EXPIRES_IN=86400(24h), BCRYPT_ROUNDS=10

**User 模型:**
```javascript
// findByUsername(username) → User | undefined
// create({ username, passwordHash }) → User
// clear() — 测试用
```

**种子数据:**
```javascript
// seedDatabase() — 创建 admin 用户，密码 admin123
// 幂等性：已存在则跳过
```

### Iter 3 — 服务层

**authService.js:**
- `login({ username, password })` → `{ token }`
- 用户不存在 → throw `Errors.INVALID_CREDENTIALS`
- 密码错误 → throw `Errors.INVALID_CREDENTIALS`（同上的错误）

### Iter 4 — HTTP 接口

**POST /api/auth/login:**
- 请求体: `{ username, password }`
- 成功 200: `{ token }`
- 参数缺失 400: `{ error: "用户名和密码不能为空" }`
- 登录失败 401: `{ error: "用户名或密码错误" }`
- 服务器错误 500: `{ error: "服务器内部错误" }`

---

## 三、验收标准

| # | 验收项 | 所在迭代 |
|---|--------|---------|
| 1 | AppError 正确构造 | Iter 1 |
| 2 | bcrypt 哈希和验证 | Iter 1 |
| 3 | JWT 签发和验证 | Iter 1 |
| 4 | User 模型增删查 | Iter 2 |
| 5 | 种子数据幂等性 | Iter 2 |
| 6 | 登录业务逻辑正确 | Iter 3 |
| 7 | 参数校验返回 400 | Iter 4 |
| 8 | 密码错误返回 401 | Iter 4 |
| 9 | 用户不存在返回 401 | Iter 4 |
| 10 | 完整 HTTP 流程 | Iter 4 |
| 11 | 全部 25 测试通过 | Iter 5 |