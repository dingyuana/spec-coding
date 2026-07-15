# Iter 3：服务层——登录业务逻辑

> **场景带入 → 发现问题 → 方案迭代 → 原理拆解 → 效果对比 → 情绪升华**

---

> Iter 2 我们有了 User 模型和种子数据，Iter 1 有了密码和 JWT 工具。现在把它们串起来——**写登录业务逻辑**。
>
> 只做 **1 个文件**：`services/authService.js`，外加 3 条测试。

---

## 一、你肯定遇到过的问题

登录业务逻辑看起来很简单："查用户 → 验密码 → 签 JWT → 返回 token"。三行代码的事。

但实际写起来，你可能会遇到：

- 查不到用户时直接返回 404——但 SPEC 要求 401
- 密码错误和用户不存在返回不同的错误消息——**给了攻击者枚举用户的线索**
- 签 JWT 时忘了传 `user_id`——payload 里没有用户信息，前端拿不到当前用户 ID

**一个登录函数只有 5 行，但这 5 行决定了系统的安全性。**

## 二、为什么要把业务逻辑单独拆一层？

最直接的做法：把登录逻辑写在控制器里。

```javascript
// 控制器里直接查数据库
async login(ctx) {
  const user = await db.query('SELECT * FROM users WHERE username = ?', [username]);
  if (!user) { ctx.status = 401; return; }
  // ...
}
```

**问题：** 测试这个函数需要启动数据库、插入用户、发 HTTP 请求。**太慢了，而且依赖太多。**

所以我们要把"业务逻辑"单独拆到 `services/` 层，让控制器只做"参数校验 + 格式化响应"，服务层只做"业务判断"。

![](imgs/07/01-mock-isolation.svg)

## 三、先写测试：mock 掉所有外部依赖

测试服务层的关键技巧：**不依赖真实的模型、密码、JWT，全部用 mock 替代。**

```javascript
// tests/unit/authService.test.js
const mockUserModel = { findByUsername: jest.fn() };
const mockPassword = { verifyPassword: jest.fn() };
const mockJwt = { signToken: jest.fn() };

jest.mock('../../src/models/user', () => mockUserModel);
jest.mock('../../src/utils/password', () => mockPassword);
jest.mock('../../src/utils/jwt', () => mockJwt);
```

**为什么？** 因为我们要测的是"登录的逻辑"，不是"数据库能用吗"。“密码加密对吗"、"JWT 签名对吗"。那些已经在 Iter 1 和 Iter 2 测过了。**这里只测"当用户存在时干什么、不存在时干什么"。**

### 写测试（RED）

```javascript
it('用户名密码正确应返回 token', async () => {
  mockUserModel.findByUsername.mockReturnValue({ id: 1, passwordHash: 'hash' });
  mockPassword.verifyPassword.mockResolvedValue(true);
  mockJwt.signToken.mockReturnValue('valid-token');

  const result = await AuthService.login({ username: 'admin', password: 'admin123' });
  expect(result).toEqual({ token: 'valid-token' });
});
```

这条测试覆盖了"用户存在 → 密码正确 → 返回 token"的 happy path。注意 `signToken` 被调用时传的是 `1`（用户 ID），不是用户对象，不是字符串。

```javascript
it('密码错误应抛出 INVALID_CREDENTIALS', async () => {
  mockUserModel.findByUsername.mockReturnValue({ id: 1, passwordHash: 'hash' });
  mockPassword.verifyPassword.mockResolvedValue(false);

  await expect(AuthService.login({ username: 'admin', password: 'wrong' }))
    .rejects.toMatchObject({ statusCode: 401 });
});

it('用户不存在应抛出 INVALID_CREDENTIALS（与密码错误相同）', async () => {
  mockUserModel.findByUsername.mockReturnValue(undefined);

  await expect(AuthService.login({ username: 'ghost', password: 'x' }))
    .rejects.toMatchObject({ statusCode: 401, message: '用户名或密码错误' });
});
```

**关键：** 两条测试都断言 `statusCode: 401`，且消息相同。这是 SPEC 里"防枚举攻击"的要求——攻击者无法通过错误消息判断"这个用户存在但密码错了"还是"这个用户不存在"。

### 写实现（GREEN）

```javascript
// src/services/authService.js
const AuthService = {
  async login({ username, password }) {
    const user = UserModel.findByUsername(username);
    if (!user) throw Errors.INVALID_CREDENTIALS;        // 用户不存在
    const isValid = await verifyPassword(password, user.passwordHash);
    if (!isValid) throw Errors.INVALID_CREDENTIALS;      // 密码错误
    const token = signToken(user.id);
    return { token };
  },
};
```

**5 行代码，3 个分支：**

![](imgs/07/02-login-flow.svg)

| 条件 | 结果 |
|------|------|
| 用户不存在 | `throw Errors.INVALID_CREDENTIALS`（401） |
| 密码错误 | `throw Errors.INVALID_CREDENTIALS`（401，**相同错误**） |
| 都通过 | 签 JWT，返回 `{ token }` |

第 2 行和第 3 行抛出**完全相同的错误对象**。这不是巧合，是 SPEC 第 4 条业务规则的要求。

**跑测试：** `npx jest tests/unit/authService.test.js` → 3 条全绿 ✅

## 四、Iter 3 的本质：mock 让测试变快

没有 mock 的测试：要启动数据库、要创建用户、要连 JWT 服务——**跑一次 5 秒。**

有 mock 的测试：只测业务逻辑，不依赖任何外部服务——**跑一次 0.1 秒。**

**3 条测试，100% 分支覆盖。**

## 五、验证

```bash
$ npx jest tests/unit/
Tests: 21 passed, 21 total ✅
```

## 六、进入 Iter 4

服务层写好了，接下来把业务逻辑暴露成 HTTP 接口——**控制器 + 路由 + 错误处理。**

```
Tests: 21 passed, 21 total ✅
```

---

*下一篇：08-Iter 4——HTTP 接口层。*