# Iter 5：完整验证 + 回顾——30 条测试全部通过

> **场景带入 → 发现问题 → 方案迭代 → 原理拆解 → 效果对比 → 情绪升华**

---

> **最后一个迭代：不写新代码。只做一件事——让 30 条测试全部绿。**
>
> **如果你跳过前面的步骤直接在这里打开终端，请先确保：**
>
> ```bash
> npm install
> cp .env.example .env    # 如果还没配置
> ```
>
> **然后输入：**
>
> ```bash
> npm test
> ```

---

## 一、"做完"但心慌——你敢说你的代码真的对吗？

写完了功能。手动 curl 了两下。返回了正确的 JSON。

你关掉终端。长吁一口气。告诉自己"做完了"。

**但你心里清楚：你只测了最常用的那一条路。**

- 密码错误你试了 —— 但用户不存在呢？响应体和密码错误完全一样吗？
- 参数完整你测了 —— 但少传 `username` 呢？少传 `password` 呢？两个都为空字符串呢？
- Token 返回了你看到了 —— 但 payload 里真的有 `user_id` 吗？24 小时后会过期吗？签名被篡改你能检测到吗？

**这些"万一"，你一个都没测。**

你不是懒。你只是太累了。从 Iter 0 一路写到 Iter 4，脑子里装了 12 个文件、4 个 Scenario、无数个边界条件。手动验证？你撑死能跑三个例子。

**但你的代码——在一个你没注意到的角落——可能正在静悄悄地错着。**

---

## 二、从 0 到 30：让仪式感见证成长

你现在做的，不是"跑个测试看看"。**你在做一件有仪式感的事：把过去 5 个迭代积累的所有判断力，交给机器一次性验证。**

输入：

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

**2.2 秒。30 条测试。全部通过。**

![](imgs/09/02-test-distribution.svg)

等一下。回味一下这行字的重量：

> **Tests: 30 passed, 30 total**

这不是 30 条随便写的断言。这是 **13 条单元测试 + 9 条服务测试 + 8 条集成测试**，覆盖了整个登录模块的每一层：

| 文件 | 数量 | 守护什么 |
|------|------|---------|
| `tests/unit/errors.test.js` | 6 | 错误类构造、预定义错误码、堆栈捕获 |
| `tests/unit/password.test.js` | 4 | bcrypt 哈希、密码长度边界、验证匹配 |
| `tests/unit/jwt.test.js` | 3 | Token 签发格式、payload 完整性、过期验证 |
| `tests/unit/userModel.test.js` | 5 | 用户增删查、存在/不存在、清空重置 |
| `tests/unit/authService.test.js` | 3 | 登录成功、密码错误、用户不存在（同一个错误） |
| `tests/integration/auth.test.js` | 8 | 4 个 Scenario 的 HTTP 完整路径 + 边界条件 |

**每条测试的名字都是一段故事：**

```
✓ 错误消息与密码错误完全一致（防枚举）
✓ 密码少于 6 位时应抛出错误
✓ JWT payload 应包含 user_id
✓ 缺少 password 应返回 400
```

**从 Iter 0 的 0 条测试，到现在的 30 条——每一步都在往这道护城河里添砖加瓦。** 如果你是从头跟到现在的，这 30 个绿色 ✅ 就是你的勋章。

---

## 三、追查链：SPEC → 测试 → AGENT——三层约束的威力

现在我们要做一件很酷的事。我们把一条"密码错误"的路径，从 SPEC 到测试到 AGENT，完整追查一遍。

### 第 1 层：SPEC 说——契约

打开 `SPEC.md`：

```
### Scenario 2: 密码错误
- Given 数据库中存在用户 admin
- When 用户提交正确的用户名但错误的密码
- Then 返回 401
- And 响应体为 `{ "error": "用户名或密码错误" }`
```

**这是业务方的承诺："API 长这样，客户端按这个格式解析。"**

### 第 2 层：测试验证——门禁

打开 `tests/integration/auth.test.js`：

```javascript
it('应返回 401 和错误消息', async () => {
  const res = await request(app.callback())
    .post('/api/auth/login')
    .send({ username: 'admin', password: 'wrongpass' });

  expect(res.status).toBe(401);
  expect(res.body.error).toBe('用户名或密码错误');
});
```

**这是一道自动化门禁：SPEC 里的每一个"Then"，都有对应的 `expect` 在蹲守。**

### 第 3 层：AGENT 约束——规范

打开 `AGENT.md`：

```
## 禁止事项
| 禁止 | 原因 |
|------|------|
| 登录泄露用户是否存在 | 防枚举攻击 |
```

**这是比测试更早的约束：在写任何代码之前，AGENT 就已经写死了"你不能做什么"。**

### 追查链闭环

```
SPEC 说：密码错误返回 401 { error }
  ↓ 测试检验
auth.test.js 第 N 行：expect(res.status).toBe(401)
  ↓ 代码实现
authController.js：ctx.body = { error: err.message }
  ↓ 规范约定
AGENT 第 13 行：禁止登录泄露用户是否存在
```

**我再说清楚一点：**

这条链意味着什么？

- **改 SPEC** → 测试立刻报错（契约变了，门禁没更新）
- **改测试** → 代码逻辑对不上（红在 CI）
- **改代码** → AGENT 的规范作为最后一道防线（如果忘了写测试，至少 AGENT 还在）

**三层，层层锁定。这不是"以防万一"，这是"万无一无"。**

---

## 四、6 个迭代：回头看，每一步都是里程碑

现在站在 Iter 5 往回看——这 6 个迭代像不像你爬了 6 段台阶？

### Iter 0 — 搭好工程底座

**产出：** SPEC.md / PLAN.md / AGENT.md / package.json / .env / .gitignore

**0 行代码，6 个文件，0 条测试。**

没有写任何业务逻辑，但你做了最重要的事：**想清楚再动手。**

### Iter 1 — 工具函数层

**产出：** errors.js / password.js / jwt.js + 3 个测试文件

**测试：0 → 13 ✅ （+13）**

这是整个项目的基础层。bcrypt 哈希、JWT 签发、自定义错误类——每一段代码都被单元测试锁死。

```javascript
// 密码少于 6 位 → 直接拒绝
it('密码少于 6 位时应抛出错误')
```

**边界条件从 Iter 1 就开始守护了。**

### Iter 2 — 数据模型 + 种子数据

**产出：** config/index.js + user.js + seed.js

**测试：13 → 18 ✅ （+5）**

User 模型的增删查、种子数据的幂等性。你学会了"先清空、再播种、再验证"的模式。

### Iter 3 — 服务层

**产出：** authService.js

**测试：18 → 21 ✅ （+3）**

这是第一次使用 Mock 隔离测试——没有网络、没有数据库，只有纯业务逻辑的验证。

```javascript
it('密码错误应抛出 INVALID_CREDENTIALS')
it('用户不存在应抛出 INVALID_CREDENTIALS')
```

**注意：两条测试抛同一个错误。这就是 SPEC 里"防枚举"的落地。**

### Iter 4 — HTTP 接口层

**产出：** errorHandler.js / authController.js / routes/auth.js / app.js / index.js

**测试：21 → 30 ✅ （+9，其中 8 条是集成测试）**

控制器、路由、错误处理器、应用装配——每一层都有清晰的边界。

**从 Iter 4 开始，你可以真的 curl 了：**

```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
# → {"token":"eyJhbGciOiJIUzI1NiIs..."}
```

### Iter 5 — 完整验证（就是现在）

**测试：30 passed, 30 total ✅**

**没有新代码。只有验证。**

---

```
迭代里程碑：

Iter 0: SPEC / PLAN / AGENT / 脚手架     → 搭好框架   测试：0
  ↓
Iter 1: 工具函数（3 文件，13 测试）      → 13 passed ✅   +13
  ↓
Iter 2: 数据模型 + 种子（2 文件，5 测试）→ 18 passed ✅   +5
  ↓
Iter 3: 服务层（1 文件，3 测试）         → 21 passed ✅   +3
  ↓
Iter 4: HTTP 接口（5 文件，8 测试）      → 30 passed ✅   +9
  ↓
Iter 5: 完整验证                         → 30 passed ✅   全绿
```

**每个 Iter 结束时，测试数都在增加，但全部是绿色。**

这不是巧合。**这不是"恰好通过"，而是"有意识地通过"**——每条测试都是在写代码之前就规划好的，每个边界条件都是 SPEC 提前定义的。

---

## 五、手动验证——用你的手指感受三层约束

如果你像我一样，不相信自动化测试的结果（"万一测试写错了呢？"），那你还可以亲手试试。

启动服务：

```bash
npm run dev
```

然后在另一个终端：

```bash
# 正常登录
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
# → {"token":"eyJhbGciOiJIUzI1NiIs..."}

# 密码错误
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrongpass"}'
# → {"error":"用户名或密码错误"}

# 用户不存在
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"ghost","password":"x"}'
# → {"error":"用户名或密码错误"}   ← 和上面完全一样！

# 参数缺失
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{}'
# → {"error":"用户名和密码不能为空"}
```

**注意到了吗？** 第二条和第三条返回的错误消息**完全一样**。这就是 AGENT 要求"禁止登录泄露用户是否存在"的具体体现——攻击者无法通过错误消息差异来枚举有效用户名。

**现在，对比一下测试输出和手动输出。你会发现它们完全一致。** 这就是"机器替你手工测试"——30 条测试在 2 秒内跑完了你 5 分钟才能 curl 完的路径。

---

## 六、三个月后——测试的真正价值

让我们做个思想实验。

三个月后，一个新同事接手这段代码。需求变了：登录响应必须加上 `expires_in` 字段。

他改完 `authController.js`：

```javascript
// 旧：ctx.body = { token };
// 新：ctx.body = { token, expires_in: config.jwt.expiresIn };
```

他自信满满。一跑测试：

```
Scenario 1: 正常登录
  ✓ admin 正确密码应返回 200 和 JWT token
  ✓ JWT payload 应包含 user_id             ✅（仍然通过）
```

等等——测试居然通过了？**不对啊，响应体多了一个字段，前端的接口文档更新了吗？**

这就是"添加字段"的情景——**测试没有失败，因为它只断言了"必须有 token"，没有断言"必须没有 expires_in"。** 这是好事，说明改进没有破坏现有契约。

但你换一个情景：

他改完 `authController.js`：

```javascript
// 旧：{ token }
// 新：{ data: { token }, code: 200 }   ← "我觉得这样更规范"
```

一跑测试：

```
Scenario 1: 正常登录
  ✕ admin 正确密码应返回 200 和 JWT token
    Expected res.body.token to be defined
    Received: undefined
```

**2 分钟就知道改坏了什么。**

- ❌ 不需要手动 curl
- ❌ 不需要问同事"这个接口格式是什么"
- ❌ 不需要等 QA 测出来
- ❌ 不需要上线之后崩溃

**这就是 30 条测试的真正价值：不是"证明你写对了"，而是"证明别人没改坏"。**

```text
SDD 让你想清楚了再做
TDD 让你做对了再改
测试让你改完了还放心
```

---

## 七、不是代码写完了，是你学会了怎么设计代码

站在这里往回看，你做了什么？

**你不是写了 12 个文件、30 条测试、6 个迭代。**

**你是学会了一种设计代码的方式：**

1. **先写 SPEC**：把需求变成契约，而不是对话记录
2. **再写 PLAN**：把任务排成迭代，每个迭代结束都有里程碑
3. **再写 AGENT**：把规范写成门禁，不是靠记忆力而是靠文件
4. **再写测试**：把"人工验证"升级为"自动化门禁"
5. **再写代码**：让每一行代码都有对应的约束

**这套方法论有一个名字：SDD（Spec-Driven Development）+ TDD（Test-Driven Development）。**

它不适合所有项目——一个 3 天的原型不需要 30 条测试。**但对于任何"要上线、要维护、要交接"的项目，这套流程是把不确定性降到最低的方法。**

六个月后，你不会记得 `app.js` 里 `bodyParser` 和 `try-catch` 的顺序。

但你会记得：**先想清楚，再做。做对了，再改。改完了，还有测试帮你守着。**

---

> **全文完。**
>
> 从 Iter 0 的空白文件，到 Iter 5 的 30 条测试全部通过，这条路你走完了。
>
> 你在 6 个迭代里学会了：
> - 如何用 SPEC 把需求写成不会模棱两可的契约
> - 如何用 PLAN 把大任务切成可交付的小步骤
> - 如何用 AGENT 把规范写成不可突破的门禁
> - 如何用 TDD 让每一行代码都有对应测试
> - 如何用分层架构让每个组件各司其职
>
> **你不再只是"写代码的人"——你是"设计代码的人"。**
>
> 如果你愿意，这个故事可以从这里继续——用同样的方法写下一个模块。框架已经搭好了，门禁已经打开了，你需要的只是再写一本 SPEC。
>
> **下一篇：没有下一篇了。你站在了起点。**