# Iter 4：HTTP 接口层——让登录接口真正可用

> **场景带入 → 发现问题 → 方案迭代 → 原理拆解 → 效果对比 → 情绪升华**

---

## 一、你肯定踩过的坑：控制器里直接调 Service

服务层写好了，模型写好了，工具函数也准备好了。你满心欢喜，十几行代码把登录接口挂上——


```javascript
// ❌ 反面教材：你肯定写过这样的代码
router.post('/login', async (ctx) => {
  const { token } = await AuthService.login(ctx.request.body);
  ctx.body = { token };
});
```


看起来干净利落。跑一下，好像也能用。

但你真的敢把这代码上线吗？

**问题 1：参数呢？** 如果前端没传 `username`，`ctx.request.body.username` 是 `undefined`。`findByUsername(undefined)` 返回 `undefined`，然后 `bcrypt.compare` 直接崩溃，最后返回一个 500。**但这里的问题是前端传参不规范，不是服务器出错了——你应该返回 400，而不是 500。**

**问题 2：异常呢？** 如果 `AuthService.login` 抛出"密码错误"，Koa 默认的异常处理把它当成 500 返回。**密码错误和服务器宕机，前端收到的是同一个 500——这怎么让客户端区分？**

**这是 HTTP 接口层最容易被忽视、也最致命的两个问题。**

> 参数校验是接口的"安检门"，错误处理是系统的"安全气囊"。少了任何一个，用户体验和系统可靠性都会崩塌。

所以，Iter 4 要做的，就是在路由和 service 之间，插进去两个关键层：

```
HTTP 请求
  │
  ▼
┌─────────────────────┐
│  路由 (Router)       │  ← 把 URL 映射到控制器
├─────────────────────┤
│  控制器 (Controller) │  ← 参数校验 → 调 service → 格式化响应
├─────────────────────┤
│  服务层 (Service)    │  ← 业务逻辑（你已经在 Iter 3 写好了）
├─────────────────────┤
│  模型层 (Model)      │  ← 数据存取
└─────────────────────┘
  │
  ▼
  错误处理器 (Error Handler)  ← 统一拦截所有异常，转成 JSON
```

**控制器的边界：** 只做三件事——(1) 校验参数格式，(2) 调用 service，(3) 格式化响应。不做"查数据库"（那是 model 的事），不做"密码比较"（那是 service 的事）。

**错误处理器的边界：** 把所有异常统一拦截，`AppError` 返回业务错误码，非 `AppError` 返回通用 500。**绝不暴露堆栈。**

![](imgs/08/01-traceability-chain.svg)

---

## 二、先写测试：4 个 Scenario 的"场景感"

在动手写代码之前，先写集成测试。这是整个教程最大的一条测试文件——**8 条测试，覆盖 SPEC 定义的 4 个 Scenario**。

打开 `tests/integration/auth.test.js`。

```javascript
// 每次测试前：清空数据 → 预置 admin → 创建新应用
beforeEach(async () => {
  UserModel.clear();
  await seedDatabase();
  app = createApp();
});
```

每条测试都模拟"真实用户发 HTTP 请求"——用的是 `supertest`，发的是真的 `POST /api/auth/login`。

---

### Scenario 1：正常登录——"我是 admin，密码正确，请放行"

```javascript
it('admin 正确密码应返回 200 和 JWT token', async () => {
  const res = await request(app.callback())
    .post('/api/auth/login')
    .send({ username: 'admin', password: 'admin123' });

  expect(res.status).toBe(200);
  expect(res.body.token).toBeDefined();
  expect(res.body.token.split('.')).toHaveLength(3);  // JWT 三段式
});
```

**为什么断言 token 有 3 段？** JWT 格式是 `header.payload.signature`，用 `.` 分隔。如果返回的不是 3 段，说明 JWT 格式有问题。

这条断言在 Semgrep 和 linter 里都找不到，但它准确捕捉了"JWT 结构完整性"。**这是经验沉淀出来的测试，不是工具能自动生成的。**

---

### Scenario 2：密码错误——"我记错密码了，告诉我哪里错了，但别告诉我是哪个字段"

```javascript
it('应返回 401 和错误消息', async () => {
  const res = await request(app.callback())
    .post('/api/auth/login')
    .send({ username: 'admin', password: 'wrongpass' });

  expect(res.status).toBe(401);
  expect(res.body.error).toBe('用户名或密码错误');
});
```

注意：错误消息是"用户名或密码错误"，不是"密码错误"——这是安全设计，防止攻击者通过错误消息推断"用户名存在"。

---

### Scenario 3：用户不存在 + 防枚举——"ghost 用户不存在，但响应和密码错误完全一样"

```javascript
it('错误消息与密码错误完全一致（防枚举）', async () => {
  const [wrongPass, notFound] = await Promise.all([
    request(app.callback()).post('/api/auth/login').send({ username: 'admin', password: 'wrong' }),
    request(app.callback()).post('/api/auth/login').send({ username: 'ghost', password: 'x' }),
  ]);

  expect(wrongPass.body).toEqual(notFound.body);  // ✅ 完全相同
});
```

这条测试的精妙之处在于两点：

1. **`Promise.all` 并发执行**——两条请求同时发出，模拟真实场景下的并发流量。
2. **`toEqual` 断言"两个响应体完全一致"**——不仅仅是状态码一样，body 里的内容也必须一样。如果哪天有人改了密码错误的消息格式但忘了改用户不存在的，这条测试会立刻报错。

**这是防枚举攻击的护栏。** 攻击者无法通过错误消息的差异来推断"用户名是否存在"。

---

### Scenario 4：参数缺失——"前端没传 username，我该返回什么？"

```javascript
it('缺少 username 应返回 400', async () => {
  const res = await request(app.callback())
    .post('/api/auth/login')
    .send({ password: 'admin123' });
  expect(res.status).toBe(400);
  expect(res.body.error).toBe('用户名和密码不能为空');
});

it('两个字段都缺失应返回 400', async () => {
  const res = await request(app.callback())
    .post('/api/auth/login')
    .send({});
  expect(res.status).toBe(400);
});

it('字段为空字符串也应返回 400', async () => {
  const res = await request(app.callback())
    .post('/api/auth/login')
    .send({ username: '', password: '' });
  expect(res.status).toBe(400);
});
```

**8 条测试，跑一遍 ≈ 1.5 秒。** 快到每次保存文件后都可以跑一遍，确保没有回退。

---

## 三、写代码：分层架构的边界之美

### 错误处理器——统一 JSON 格式的"安全气囊"

```javascript
// src/middleware/errorHandler.js
function errorHandler(err, ctx) {
  if (err instanceof AppError) {
    ctx.status = err.statusCode;
    ctx.body = { error: err.message };  // 统一 JSON 格式
    return;
  }
  // 未预期的错误，不暴露内部细节
  ctx.status = 500;
  ctx.body = { error: '服务器内部错误' };
}
```

这里有两个分支，**它们的区别定义了整个系统的错误处理策略：**

| 分支 | 触发条件 | 返回给前端 |
|------|---------|-----------|
| `AppError` | 业务逻辑主动抛出的异常（如"密码错误"） | 业务错误码 + 友好消息 |
| 非 `AppError` | 未预期的异常（如数据库崩溃、网络超时） | **500 + "服务器内部错误"** |

**为什么非 `AppError` 不暴露堆栈？** 因为堆栈信息会暴露系统内部结构——文件路径、函数名、数据库表名——这些是攻击者的情报金矿。**所有非预期的错误，统一吞掉，只返回"服务器内部错误"。**

---

### 控制器——参数校验的"安检门"

```javascript
// src/controllers/authController.js
async login(ctx) {
  const { username, password } = ctx.request.body;

  // 第 1 层：参数校验
  if (!username || !password) {
    throw Errors.MISSING_PARAMS('用户名和密码不能为空');
  }

  // 第 2 层：调 service
  const { token } = await AuthService.login({ username, password });

  // 第 3 层：格式化响应
  ctx.status = 200;
  ctx.body = { token };
}
```

**控制器的职责边界清晰到可以用一句话概括：** 第 3-5 行是"参数校验"，第 7 行是"调 service"，第 9-10 行是"格式化响应"。

不做什么？不查数据库（那是 model 的事），不比较密码（那是 service 的事），不处理异常（那是 errorHandler 的事）。

**这就是分层架构的边界之美：每一层只做一件事，每一件事都只有一个地方做。**

---

### 路由——极简的"交通指示牌"

```javascript
// src/routes/auth.js
router.post('/login', AuthController.login);
```

就这么一句话。路由不包含任何业务逻辑，它只是告诉系统：**"POST /login 请求，交给 AuthController.login 处理。"**

---

### 应用工厂——组装所有中间件

```javascript
// src/app.js
function createApp() {
  const app = new Koa();
  app.use(bodyParser());           // 中间件 1：解析 JSON 请求体
  app.use(async (ctx, next) => {   // 中间件 2：全局 try-catch
    try { await next(); }
    catch (err) { errorHandler(err, ctx); }
  });
  app.use(authRouter.routes());    // 中间件 3：注册路由
  return app;
}
```

**第 5-7 行的 `try-catch` 是整个系统的"安全底线"。** 没有这一层，任何抛出的错误都会导致 Koa 返回 500。所有 `throw Errors.XXX` 都会被这里捕获，交给 `errorHandler` 转成正确的状态码。

中间件的顺序也很重要：`bodyParser` 必须在路由之前，否则路由拿不到 `ctx.request.body`；`try-catch` 必须在路由之前，否则路由抛出的错误无法被捕获。

![](imgs/08/02-layer-architecture.svg)

---

## 四、验证：30 passed，全部通过

```bash
$ npx jest tests/integration/auth.test.js
Tests: 8 passed, 8 total ✅
```

8 条集成测试，覆盖 4 个 Scenario，全部通过。

但这还不够——让我们跑整个测试套件：

```bash
$ npm test
Test Suites: 6 passed, 6 total
Tests:       30 passed, 30 total ✅
```

**30 条测试，全部通过。** 从 Iter 1 的单元测试，到 Iter 2 的模型测试，到 Iter 3 的服务层测试，再到 Iter 4 的集成测试——所有代码都在测试的护城河之内。

这一刻，你不仅有了一个能用的登录接口，你还有了：

- **8 条集成测试**，覆盖正常登录、密码错误、用户不存在、参数缺失 4 个 Scenario
- **统一的错误处理**，`AppError` 返回业务错误码，非 `AppError` 返回 500
- **清晰的参数校验**，所有接口入口都有"安检门"
- **分层架构的边界**，controller/service/model 各司其职

---

## 五、进入 Iter 5

代码写完了。HTTP 接口层有了，控制器有了，错误处理有了，集成测试有了。

最后一个迭代——**完整验证 + 回顾**。

```
Tests: 30 passed, 30 total ✅
```

---

*下一篇：09-Iter 5——完整验证 + 回顾。*