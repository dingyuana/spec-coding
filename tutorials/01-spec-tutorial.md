# 把需求写成契约——SPEC.md

> **你的代码没炸，只是因为你还没上线。**

---

## 一、「你翻一下代码，在第 47 行」

你问同事：「登录接口返回什么格式？」

他头也不抬：「嗯……我翻一下代码。哦，在第 47 行，返回 `{ token }`。」

你信了。写进前端，联调通过，上线。

三天后线上告警：**全部登录失败**。

你翻 Git 记录——有人改了后端，返回变成 `{ data: { token } }`。没人通知你，没有文档，没有邮件，什么都没有。你盯着 Slack 上三天前那句「在第 47 行」咬牙切齿。

**这不叫沟通问题。这叫你们之间没有一份具备法律效力的契约。**

---

## 二、你天真地写了 README，然后呢？

被坑过一次之后，你在 README 里加了一段：

```markdown
## API
- POST /api/auth/login → 返回 token
```

写完觉得踏实了。文档都有了，再出事不怪我了吧？

一周后你又上线了。又炸了。

你跑去一看——代码改了，README 还挂着那条优雅的 Markdown，像一块墓碑。

**Readme 是「描述」，不是「契约」。** 描述是写给路过的人看的，过期了就过期了，没人会为它负责。它像一张贴在墙上的便利贴——方便，但谁都可以无视它。

你要的是一份**双方签字画押的合同**，甲方违约了，乙方能拿着合同去拍桌子。

---

## 三、真正的合同叫 SPEC

所以你需要的不是 `README.md`，而是 `SPEC.md`。

SPEC 不是「记录」，它是**合同**。白纸黑字，写清楚每一种情况。不仅是「正常情况」，更重要的是那些**让你半夜起来修 Bug 的边界情况**。

---

## 四、本项目 SPEC.md 长什么样

打开 `/root/spec-coding/SPEC.md`，最核心的是 **4 个 Scenario**——每个 Scenario 覆盖一条业务路径，包括正常路径和所有异常路径：

```markdown
# 用户登录模块 — SPEC（全局契约）

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
```

看到 Scenario 2 和 Scenario 3 返回**同一个错误信息**（`用户名或密码错误`）了吗？这**不是笔误**——这是安全设计。你告诉攻击者「用户不存在」，等于给了他一本花名册。SPEC 把这种细节写死，防止任何人「拍脑袋改一下」。

---

## 五、SPEC 中的迭代规划

SPEC 不止定义接口契约，还定义了整个项目的**迭代路线**。每个迭代只实现 SPEC 的一部分：

```
### Iter 1 — 工具函数接口
errors.js:     AppError(message, statusCode) + 预定义错误常量
password.js:   hashPassword(plain) → hash / verifyPassword(plain, hash) → boolean
jwt.js:        signToken(userId) → token / verifyToken(token) → payload

### Iter 2 — 数据模型 + 配置
config/index.js:  .env 读取（PORT, JWT_SECRET, JWT_EXPIRES_IN, BCRYPT_ROUNDS）
User 模型:        findByUsername / create / clear
种子数据:         seedDatabase() — 预置 admin 用户

### Iter 3 — 服务层
authService.js: login({ username, password }) → { token }
                用户不存在/密码错误 → throw Errors.INVALID_CREDENTIALS（同一错误）

### Iter 4 — HTTP 接口
POST /api/auth/login:
  成功 200: { token }
  参数缺失 400: { error: "用户名和密码不能为空" }
  登录失败 401: { error: "用户名或密码错误" }
  服务器错误 500: { error: "服务器内部错误" }
```

每个迭代的「验收标准」也写在 SPEC 里，共 11 条验收项，逐一对应测试：

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

---

## 六、SPEC → 测试：每个 Scenario 都有一条真实的测试

普通的文档写完了就躺在那，等着腐烂。SPEC 不一样。

**SPEC 里每一条约定，最终都会变成一条测试用例。** 让我们打开本项目真实的集成测试文件，看看每个 Scenario 是如何被翻译成测试的。

以下是 `tests/integration/auth.test.js` 中的完整测试结构：

### Scenario 1 → 正常登录

```javascript
// tests/integration/auth.test.js — Scenario 1
describe('Scenario 1: 正常登录', () => {
  it('admin 正确密码应返回 200 和 JWT token', async () => {
    const res = await request(app.callback())
      .post('/api/auth/login')
      .send({ username: 'admin', password: 'admin123' });
    expect(res.status).toBe(200);
    expect(res.body.token).toBeDefined();
    expect(res.body.token.split('.')).toHaveLength(3);  // JWT 是三段式
  });

  it('JWT payload 应包含 user_id', async () => {
    const res = await request(app.callback())
      .post('/api/auth/login')
      .send({ username: 'admin', password: 'admin123' });
    const decoded = jwt.verify(res.body.token, config.jwt.secret);
    expect(decoded.user_id).toBe(1);
  });
});
```

### Scenario 2 → 密码错误

```javascript
// tests/integration/auth.test.js — Scenario 2
describe('Scenario 2: 密码错误', () => {
  it('应返回 401 和错误消息', async () => {
    const res = await request(app.callback())
      .post('/api/auth/login')
      .send({ username: 'admin', password: 'wrongpass' });
    expect(res.status).toBe(401);
    expect(res.body.error).toBe('用户名或密码错误');
  });
});
```

### Scenario 3 → 用户不存在

```javascript
// tests/integration/auth.test.js — Scenario 3
describe('Scenario 3: 用户不存在', () => {
  it('应返回 401', async () => {
    const res = await request(app.callback())
      .post('/api/auth/login')
      .send({ username: 'hacker', password: 'x' });
    expect(res.status).toBe(401);
    expect(res.body.error).toBe('用户名或密码错误');
  });

  // ⭐ 防枚举验证：错误消息与密码错误完全一致
  it('错误消息与密码错误完全一致（防枚举）', async () => {
    const [wrongPass, notFound] = await Promise.all([
      request(app.callback()).post('/api/auth/login').send({ username: 'admin', password: 'wrong' }),
      request(app.callback()).post('/api/auth/login').send({ username: 'ghost', password: 'x' }),
    ]);
    expect(wrongPass.body).toEqual(notFound.body);
  });
});
```

**第 66-72 行是整个测试文件中最关键的一条测试**。它同时发送"密码错误"和"用户不存在"两个请求，然后断言两者的响应体**完全一致**。只要有人把错误消息改成了不同的文案，这条测试就会亮红灯。

### Scenario 4 → 参数缺失

```javascript
// tests/integration/auth.test.js — Scenario 4
describe('Scenario 4: 参数缺失', () => {
  it('缺少 username 应返回 400', async () => {
    const res = await request(app.callback())
      .post('/api/auth/login')
      .send({ password: 'admin123' });
    expect(res.status).toBe(400);
    expect(res.body.error).toBe('用户名和密码不能为空');
  });

  it('缺少 password 应返回 400', async () => {
    const res = await request(app.callback())
      .post('/api/auth/login')
      .send({ username: 'admin' });
    expect(res.status).toBe(400);
    expect(res.body.error).toBe('用户名和密码不能为空');
  });

  it('两个字段都缺失应返回 400', async () => {
    const res = await request(app.callback())
      .post('/api/auth/login')
      .send({});
    expect(res.status).toBe(400);
    expect(res.body.error).toBe('用户名和密码不能为空');
  });
});
```

**4 个 Scenario，8 条测试，每条测试都是 SPEC 中一行契约的可执行版本。**

---

## 七、SPEC 是可执行的文档——测试就是执法者

现在这条 401 不再是一个美好的愿望。**它是一条带有强制力的法律条文。**

![](imgs/01/01-spec-contract-framework.svg)

**SPEC 是合约，测试是执法者。**

- 只有合约没有执法者 → 文档迟早发霉
- 只有测试没有合约 → 测试写了什么全靠猜
- **合约 + 执法者** → 代码上线前就自己把自己审判了

每次 CI 跑起来，这些测试就像警察一样巡逻。谁改坏了接口？测试直接亮红灯。你不需要去问「谁改了什么」，CI 告诉你。

---

## 八、有 SPEC 和没 SPEC 的差距，不是一个 README 的距离

![](imgs/01/02-with-vs-without-spec-comparison.svg)

| 场景 | 没 SPEC（靠脸靠嘴） | 有 SPEC（靠契约靠代码） |
|------|-------------------|----------------------|
| 新同事加入 | 翻代码 + 问人 + 被白眼 | 读 SPEC，10 分钟搞懂 |
| 接口变更 | 口头通知 + 运气好知道 / 运气不好上线炸 | 改 SPEC → 改测试 → 改代码，链条完整 |
| 验收测试 | 打开 Postman 点三遍「发送」，假装测完了 | 30 条测试一键跑完，绿了就过 |
| 线上排查 | 翻日志猜字段 | 翻 SPEC 对契约，一秒定位偏差 |

没 SPEC 的时候，你的知识库长在每个人的脑子里。人走了，知识也走了。有 SPEC 的时候，知识长在代码仓库里，谁也带不走。

---

## 九、合同签好了，然后呢？

OK，合同有了，执法者（测试）也安排上了。

但问题来了——**5 个迭代，先做哪个？** 你不是一个人在战斗，你和你的队友不能各做各的，代码合到一起才发现一个做了 Iter 2，另一个也在做 Iter 2，Iter 1 还没人碰。

这就是下一篇文章要做的事。

> 🗺️ **下一篇：[02-PLAN.md——把任务排成地图。](./02-PLAN.md)**
>
> *先把路画清楚再开车，不然你以为自己在竞速，其实是在碰碰车场地里踩油门。*

---

*下一篇：02-PLAN.md——把任务排成地图。*