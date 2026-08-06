# Iter 3：服务层——为什么抽一层 + Mock 隔离测试

> **登录逻辑不到 5 行代码，但这 5 行决定了你的系统是堡垒还是纸糊的。**

---

## 一、理论：为什么抽服务层？为什么要 Mock？

### 1.1 为什么非要把业务逻辑拆一层？

最直观的做法：控制器里直接查数据库、验密码、签 JWT。一条龙搞定。

**问题来了：你怎么测这个函数？**

你要启动数据库、插入测试用户、发出 HTTP 请求、等数据库响应……一套下来 **5 秒**。测三个分支就是 15 秒。测完你还得清理数据。

更致命的是：这测试依赖了太多东西——数据库通不通？密码库对不对？JWT 签名有没有 bug？**你要测的是"登录的逻辑"，不是这些底层模块。**

所以我们要把"业务判断"从控制器里抽出来，放到 `services/` 层：

```
控制器（参数校验 + 格式化响应）
   ↕
服务层（业务逻辑判断）  ← 我们在这儿
   ↕
模型 / 工具（数据库、密码、JWT）
```

分工明确，各司其职。

### 1.2 Mock 隔离测试

**没有 mock 的测试：**

1. 启动数据库 → 等 1 秒
2. 插入种子用户 → 等 1 秒
3. 发 HTTP POST → 等 1 秒
4. 查询验证 → 等 1 秒
5. 清理数据 → 等 1 秒

**跑一次 5 秒。** 3 条测试 15 秒。等你喝杯咖啡回来，测试还没跑完。

**有了 mock：**

**跑一次 0.1 秒。** 3 条测试 0.3 秒。你连咖啡杯都不用端起来。

**为什么？** 因为 Iter 1 已经测了密码和 JWT，Iter 2 已经测了 User 模型。**这里只测"当用户存在时干什么、不存在时干什么"**——不重复测别人已经测过的东西。

Mock 的核心思想是：**用假的对象替换真实的依赖，只测试当前层的逻辑。**

![](imgs/07/01-mock-isolation.svg)

---

## 二、本项目实际代码

### 2.1 `src/services/authService.js` — 5 行逻辑，3 个分支

```javascript
// src/services/authService.js
/**
 * 认证服务
 * Iter 3: 服务层
 * 依赖：UserModel, password, jwt
 */
const UserModel = require('../models/user');
const { verifyPassword } = require('../utils/password');
const { signToken } = require('../utils/jwt');
const { Errors } = require('../utils/errors');

const AuthService = {
  async login({ username, password }) {
    const user = UserModel.findByUsername(username);
    if (!user) throw Errors.INVALID_CREDENTIALS;
    const isValid = await verifyPassword(password, user.passwordHash);
    if (!isValid) throw Errors.INVALID_CREDENTIALS;
    const token = signToken(user.id);
    return { token };
  },
};

module.exports = AuthService;
```

**5 行逻辑，3 个分支：**

| 条件 | 结果 | 说明 |
|------|------|------|
| 用户不存在 | `throw Errors.INVALID_CREDENTIALS`（401） | 和密码错误返回**完全相同**的错误 |
| 密码错误 | `throw Errors.INVALID_CREDENTIALS`（401，完全相同） | 防止枚举攻击 |
| 都通过 | 签 JWT，返回 `{ token }` | 登录成功 |

![](imgs/07/02-login-flow.svg)

### 2.3 相同错误消息防枚举

这是本项目最精妙的安全设计。很多新手犯的错误：

```javascript
// ❌ 错误做法——给攻击者送情报
if (!user) throw { message: '用户不存在', statusCode: 404 };
if (!pass) throw { message: '密码错误', statusCode: 401 };
```

现在攻击者可以写个脚本：

```
POST /api/login  username=admin   → "密码错误"      👉 用户 admin 存在，继续爆破密码
POST /api/login  username=ghost   → "用户不存在"    👉 跳过，没有这个用户
```

**这不叫登录，这叫打开大门让攻击者枚举你的用户表。**

我们的实现让所有非法登录都收到同一个回答——`Errors.INVALID_CREDENTIALS`：

```javascript
if (!user) throw Errors.INVALID_CREDENTIALS;       // 用户不存在
if (!isValid) throw Errors.INVALID_CREDENTIALS;     // 密码错误
```

第 14 行和第 16 行抛出**完全相同的错误对象**，都是 `{ statusCode: 401, message: '用户名或密码错误' }`。攻击者无从判断到底是用户名错了还是密码错了，等于在黑暗中摸瞎。

> **审美即安全，接口设计的对称性直接决定了攻击面大小。**

### 2.4 测试：`tests/unit/authService.test.js`（3 条测试，Mock 所有依赖）

```javascript
// tests/unit/authService.test.js
/**
 * 认证服务 — TDD 测试
 * Iter 3: 服务层
 * 覆盖：正常登录 / 密码错误 / 用户不存在
 */

const mockUserModel = { findByUsername: jest.fn() };
const mockPassword = { verifyPassword: jest.fn() };
const mockJwt = { signToken: jest.fn() };

jest.mock('../../src/models/user', () => mockUserModel);
jest.mock('../../src/utils/password', () => mockPassword);
jest.mock('../../src/utils/jwt', () => mockJwt);

const AuthService = require('../../src/services/authService');

describe('AuthService.login', () => {
  const mockUser = { id: 1, username: 'admin', passwordHash: 'hashed-password' };

  beforeEach(() => { jest.clearAllMocks(); });

  it('用户名密码正确应返回 token', async () => {
    mockUserModel.findByUsername.mockReturnValue(mockUser);
    mockPassword.verifyPassword.mockResolvedValue(true);
    mockJwt.signToken.mockReturnValue('valid-token');

    const result = await AuthService.login({ username: 'admin', password: 'admin123' });
    expect(mockUserModel.findByUsername).toHaveBeenCalledWith('admin');
    expect(mockPassword.verifyPassword).toHaveBeenCalledWith('admin123', 'hashed-password');
    expect(mockJwt.signToken).toHaveBeenCalledWith(1);
    expect(result).toEqual({ token: 'valid-token' });
  });

  it('密码错误应抛出 INVALID_CREDENTIALS', async () => {
    mockUserModel.findByUsername.mockReturnValue(mockUser);
    mockPassword.verifyPassword.mockResolvedValue(false);
    await expect(AuthService.login({ username: 'admin', password: 'wrongpass' }))
      .rejects.toMatchObject({ statusCode: 401, message: '用户名或密码错误' });
  });

  it('用户不存在应抛出 INVALID_CREDENTIALS', async () => {
    mockUserModel.findByUsername.mockReturnValue(undefined);
    await expect(AuthService.login({ username: 'ghost', password: 'x' }))
      .rejects.toMatchObject({ statusCode: 401, message: '用户名或密码错误' });
  });
});
```

**Mock 的设计：**

```javascript
const mockUserModel = { findByUsername: jest.fn() };
const mockPassword = { verifyPassword: jest.fn() };
const mockJwt = { signToken: jest.fn() };

jest.mock('../../src/models/user', () => mockUserModel);
jest.mock('../../src/utils/password', () => mockPassword);
jest.mock('../../src/utils/jwt', () => mockJwt);
```

三行 `jest.mock` 替换了 `authService.js` 的全部三个依赖。测试在**完全隔离**的环境中运行——不碰真实数据库、不碰真实 bcrypt、不碰真实 JWT。

**3 条测试覆盖了什么：**

| 测试 | 场景 | Mock 设置 | 断言 |
|------|------|-----------|------|
| happy path | 用户存在 + 密码正确 | findByUsername 返回用户, verifyPassword 返回 true | 返回 `{ token }` |
| password error | 密码错误 | verifyPassword 返回 false | 抛出 `{ 401, '用户名或密码错误' }` |
| user not found | 用户不存在 | findByUsername 返回 undefined | 抛出 `{ 401, '用户名或密码错误' }` |

注意第 2 条和第 3 条测试断言了**完全相同的错误对象**——这就是防枚举攻击的保证。

---

## 三、Iter 3 的本质

这一轮你学会的其实不是怎么写 5 行代码。你学会的是：

- **抽象服务层**——让控制器只做控制器的事，逻辑层只做逻辑的事
- **Mock 依赖**——不测别人的代码，只测你的判断逻辑，速度从 5 秒降到 0.1 秒
- **安全设计**——相同的错误消息不是偷懒，是故意堵住枚举攻击的路

**一段 5 行的登录函数，用对了模式就是防御堡垒，随手一写就是安全漏洞。**

---

## 四、验证：全部测试通过

```bash
$ npx jest tests/unit/

Test Suites: 5 passed, 5 total
Tests:       24 passed, 24 total ✅
```

到 Iter 3 结束，**24 条测试，全部通过。**

| Iter | 模块 | 测试条数 |
|------|------|---------|
| Iter 1 | 密码 + JWT + 错误工具 | 13 |
| Iter 2 | User 模型 | 8 |
| Iter 3 | Auth 服务层 | 3 |
| **合计** | | **24 ** |

每一条都是实打实的逻辑覆盖，没有冗余，没有依赖。**24 passed，全绿收工。** ✅

---

## 五、进入 Iter 4

服务层写好了。接下来要想办法让别人能调用它——**控制器 + 路由 + 错误处理中间件。**

```
Tests: 24 passed, 24 total ✅
```

---

*下一篇：08-Iter 4——HTTP 接口层。*