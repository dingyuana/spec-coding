# Iter 5：完整验证 + 回顾

> **场景带入 → 发现问题 → 方案迭代 → 原理拆解 → 效果对比 → 情绪升华**

---

> **最后一个迭代：不写新代码，只做一件事——跑测试。**

---

## 一、你肯定经历过这种"做完但心慌"的感觉

写完了功能，手动测了两下，返回了正确的结果。你关掉终端，告诉自己"做完了"。

但你心里清楚：**你只测了最常见的路径。**

- 密码错误你测了 —— 但用户不存在呢？
- 参数完整你测了 —— 但少传一个字段呢？
- Token 返回了你测了 —— 但 payload 里有 user_id 吗？24 小时后会过期吗？

**你能跑的那一两个例子，不代表所有场景都对了。**

## 二、跑测试：让机器替你检查 30 个场景

```bash
$ npm test
```

输出：

```
PASS tests/unit/errors.test.js          (6 条)
PASS tests/unit/password.test.js        (4 条)
PASS tests/unit/jwt.test.js             (3 条)
PASS tests/unit/userModel.test.js       (5 条)
PASS tests/unit/authService.test.js     (3 条)
PASS tests/integration/auth.test.js     (8 条)

Test Suites: 6 passed, 6 total
Tests:       30 passed, 30 total
```

**6 个测试套件，30 条测试，1.5 秒全部通过。**

![](imgs/09/02-test-distribution.svg)

这 30 条测试覆盖的不只是"正常登录"这一条路径，而是 **4 个 Scenario 的所有分支：**

| 文件 | 数量 | 守护什么 |
|------|------|---------|
| `errors.test.js` | 6 | 错误类构造、预定义错误码 |
| `password.test.js` | 4 | bcrypt 哈希、边界条件 |
| `jwt.test.js` | 3 | Token 签发格式、过期、验证 |
| `userModel.test.js` | 5 | 增删查、存在/不存在 |
| `authService.test.js` | 3 | 登录成功、密码错误、用户不存在 |
| `auth.test.js` | 8 | 4 个 Scenario 的 HTTP 完整路径 |

**30 条 = 13 条单元测试（快，独立） + 9 条服务测试（mock 依赖） + 8 条集成测试（真实 HTTP）。**

## 三、追查链：从 SPEC 到测试到 AGENT

```text
SPEC 说：密码错误返回 401 { error }
  ↓ 测试检验
auth.test.js 第 46 行：expect(res.status).toBe(401)
  ↓ 代码实现
authController.js 第 8 行：ctx.body = { error: err.message }
  ↓ 规范约定
AGENT 第 13 行：禁止登录泄露用户是否存在
```

**每一层都有对应的约束，而且这些约束是自动化、可执行的。**

## 四、手动验证

也可以在终端试试看——`npm run dev` 后：

```bash
# 正常登录
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
# → {"token":"eyJhbGciOiJIUzI1NiIs..."}

# 密码错误
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrong"}'
# → {"error":"用户名或密码错误"}
```

注意看第一个返回值——**返回的是 `{ token }` 而不是 `{ data: { token } }` 也不是 `{ code: 200, data: token }`**。这就 SPEC 里写的那样，前后端以契约为准。

## 五、完整回顾：6 个迭代

![](imgs/09/01-iteration-timeline.svg)

```
Iter 0: SPEC / PLAN / AGENT / 脚手架     → 搭好框架
  ↓
Iter 1: 工具函数（3 文件，13 测试）      → 13 passed ✅
  ↓
Iter 2: 数据模型 + 种子（2 文件，5 测试）→ 18 passed ✅
  ↓
Iter 3: 服务层（1 文件，3 测试）         → 21 passed ✅
  ↓
Iter 4: HTTP 接口（5 文件，8 测试）      → 30 passed ✅
  ↓
Iter 5: 完整验证                         → 30 passed ✅
```

**每个 Iter 结束时，测试计数都在增加，但全部是绿色。**

## 六、这条路径的意义

三个月后有人来改这段代码——比如"把登录响应从 `{ token }` 改成 `{ token, expires_in }`"。

他改完 `authController.js`，跑测试：

```
Scenario 1: 正常登录 → FAIL（期望 token 存在，但格式变了）
```

**2 分钟就知道改坏了什么。** 不需要手动 curl，不需要问同事，不需要等 QA 测，不需要上线之后才发现。

这就是 SDD + TDD 要解决的问题：**不是"代码对不对"，而是"改了之后还能不能保证对"。**

**先想清楚再做（SDD），做对了再改（TDD）。** 从零到 30 条测试全部通过，这条路你走完了。

---

⭐ **全文完。** 下一篇：没有下一篇了——你完成了整条路径。