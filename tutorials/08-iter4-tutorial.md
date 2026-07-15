# Iter 4：HTTP 接口层——让登录接口真正可用

> **场景带入 → 发现问题 → 方案迭代 → 原理拆解 → 效果对比 → 情绪升华**

---

> 服务层写好了，工具函数写好了，模型写好了——但用户怎么调用？
>
> 需要路由把 URL 映射到代码，需要控制器校验参数，需要错误处理器把异常转成 JSON。
>
> **5 个文件，8 条集成测试，覆盖 4 个 Scenario。**

---

## 一、你肯定遇到过的问题

服务层写好了，你直接把它挂在 Koa 上：

```javascript
router.post('/login', async (ctx) => {
  const { token } = await AuthService.login(ctx.request.body);
  ctx.body = { token };
});
```

好像能跑。但你漏了：

- 没校验参数——如果前端没传 `username`，`ctx.request.body.username` 是 `undefined`，`findByUsername(undefined)` 返回 `undefined`，然后返回 401——**你应该返回 400，因为这是参数问题，不是认证问题。**
- 没处理异常——如果 `AuthService.login` 抛错了，Koa 默认返回 500，不管是什么错误——**密码错误和服务器错误都返回 500，前端没法区分。**

**参数校验和错误处理，是 HTTP 接口层最容易被忽略但最重要的部分。**

![](imgs/08/01-traceability-chain.svg)

## 二、先写集成测试：4 个 Scenario 全部覆盖

打开 `tests/integration/auth.test.js`。这是最大的一条测试文件——**8 条测试覆盖了 SPEC 里定义的 4 个 Scenario。**

每条测试都在模拟"真实用户发 HTTP 请求"：

```javascript
// 每次测试前：清空数据 → 预置 admin → 创建新应用
beforeEach(async () => {
  UserModel.clear();
  await seedDatabase();
  app = createApp();
});
```

### Scenario 1：正常登录

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

**为什么断言 token 有 3 段？** JWT 格式是 `header.payload.signature`，用 `.` 分隔。如果返回的不是 3 段，说明 JWT 格式有问题。**这条断言在 Semgrep 和 linter 里都找不到，但它准确捕捉了"JWT 结构完整性"。**

### Scenario 2：密码错误

```javascript
it('应返回 401 和错误消息', async () => {
  const res = await request(app.callback())
    .post('/api/auth/login')
    .send({ username: 'admin', password: 'wrongpass' });

  expect(res.status).toBe(401);
  expect(res.body.error).toBe('用户名或密码错误');
});
```

### Scenario 3：用户不存在 + 防枚举

```javascript
it('错误消息与密码错误完全一致（防枚举）', async () => {
  const [wrongPass, notFound] = await Promise.all([
    request(app.callback()).post('/api/auth/login').send({ username: 'admin', password: 'wrong' }),
    request(app.callback()).post('/api/auth/login').send({ username: 'ghost', password: 'x' }),
  ]);

  expect(wrongPass.body).toEqual(notFound.body);  // ✅ 完全相同
});
```

**`toEqual` 断言的是"两个响应体完全一致"**——不仅仅是状态码一样，body 里的内容也一样。如果哪天有人改了密码错误的消息格式忘了改用户不存在的，这条测试会立刻报错。

### Scenario 4：参数缺失

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
```

**8 条测试跑一遍 ≈ 1.5 秒而已。**

## 三、写代码：分层组装

### 错误处理——统一 JSON 格式

```javascript
// src/middleware/errorHandler.js
function errorHandler(err, ctx) {
  if (err instanceof AppError) {
    ctx.status = err.statusCode;
    ctx.body = { error: err.message };  // 统一格式
    return;
  }
  // 未预期的错误，不暴露内部细节
  ctx.status = 500;
  ctx.body = { error: '服务器内部错误' };
}
```

第 3 行和第 8 行的区别：`AppError` 是我们自己抛的，知道错误原因（如"用户名或密码错误"），直接返回给前端。非 `AppError` 是未预期的异常（如数据库挂了），**只返回"服务器内部错误"，不暴露堆栈信息**。

### 控制器——参数校验 + 调用 service

```javascript
// src/controllers/authController.js
async login(ctx) {
  const { username, password } = ctx.request.body;
  if (!username || !password) {
    throw Errors.MISSING_PARAMS('用户名和密码不能为空');
  }
  const { token } = await AuthService.login({ username, password });
  ctx.status = 200;
  ctx.body = { token };
}
```

**控制器的职责边界很清晰：** 第 3-5 行是"参数校验"，第 6 行是"调 service"，第 7-8 行是"格式化响应"。不做"查数据库"（那是 model 的事），不做"密码比较"（那是 service 的事）。

### 路由——只有一句话

```javascript
// src/routes/auth.js
router.post('/login', AuthController.login);
```

### 应用工厂——组装所有中间件

![](imgs/08/02-layer-architecture.svg)

```javascript
// src/app.js
function createApp() {
  const app = new Koa();
  app.use(bodyParser());           // 解析 JSON 请求体
  app.use(async (ctx, next) => {   // 全局 try-catch
    try { await next(); }
    catch (err) { errorHandler(err, ctx); }
  });
  app.use(authRouter.routes());    // 注册路由
  return app;
}
```

第 5-7 行的 `try-catch` 是关键——**没有这一层，任何抛出的错误都会导致 Koa 返回 500。** 所有 `throw Errors.XXX` 都会被这里捕获，交给 `errorHandler` 转成正确的状态码。

## 四、验证

```bash
$ npx jest tests/integration/auth.test.js
Tests: 8 passed, 8 total ✅

$ npm test
Test Suites: 6 passed, 6 total
Tests:       30 passed, 30 total ✅
```

全部通过。

## 五、进入 Iter 5

代码写完了。最后一个迭代——**完整验证 + 回顾。**

```
Tests: 30 passed, 30 total ✅
```

---

*下一篇：09-Iter 5——完整验证 + 回顾。*