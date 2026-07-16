# Iter 1：工具函数层——独立可测，打好地基

> **Iter 1 是整个开发流程的起点。在这一轮里，我们只做一件事：写好三个纯工具函数，用测试把它们钉死。**

---

## 一、理论：为什么要先写工具函数？

很多新手一上来就写路由、写控制器、写数据库操作，觉得"这样才看得到效果"。但真正有经验的人会告诉你：**先写工具函数，再写业务逻辑。**

原因有三：

### 1. 工具函数是"无依赖"的——最容易被测试

工具函数（Utility Functions）不依赖数据库、不依赖网络、不依赖其他模块。它们接收输入，返回输出，是纯函数（Pure Function）。

```javascript
// 纯函数：输入确定，输出就确定，没有任何副作用
hashPassword('abc123')  // 每次结果一样（不考虑 salt 随机性）
verifyPassword('abc', hash)  // 只依赖参数，不依赖外部状态
```

这种"无依赖"的性质，让工具函数成为**整个系统里最容易测试、测试速度最快**的部分。没有数据库启动，没有 HTTP 请求，没有文件读写——跑一次测试只需要几毫秒。

### 2. 工具函数是"基石"——上层逻辑都依赖它们

看一下本项目真实的依赖关系：

```
src/services/authService.js
  ├── src/utils/password.js   ← 密码验证
  ├── src/utils/jwt.js        ← 令牌签发
  └── src/utils/errors.js     ← 错误定义
```

`authService` 依赖了 3 个工具函数。如果工具函数有 bug，整个登录流程都会崩。**地基不稳，上层越盖越危险。**

### 3. 工具函数的 Bug 通常是"边界条件"——肉眼 review 最易漏

`bcrypt.genSalt()` 没有指定 rounds 会怎样？JWT 不传 `expiresIn` 会怎样？空字符串传到密码函数里会怎样？

这些边界条件，人脑 review 的时候很容易忽略，但写测试的时候**必须**面对。测试逼你把所有边界想清楚。

> **先写工具函数，不是"搭框架"，是"把地基砸实了再往上盖"。**

---

## 二、本项目实际代码

下面展示 Iter 1 的实际代码。**所有代码块标注的是真实文件路径，内容来自本项目。**

### 2.1 `src/utils/errors.js` — 统一错误格式

```javascript
// src/utils/errors.js
/**
 * 自定义错误类
 * Iter 1: 工具函数层
 */
class AppError extends Error {
  constructor(message, statusCode = 500) {
    super(message);
    this.name = 'AppError';
    this.statusCode = statusCode;
    Error.captureStackTrace(this, this.constructor);
  }
}

const Errors = {
  INVALID_CREDENTIALS: new AppError('用户名或密码错误', 401),
  MISSING_PARAMS: (msg) => new AppError(msg, 400),
  INTERNAL: new AppError('服务器内部错误', 500),
};

module.exports = { AppError, Errors };
```

**设计要点：**
- `AppError` 继承 `Error`，保证 `instanceof Error` 成立
- `statusCode = 500` 默认值——忘记传状态码也不会爆炸
- `Errors` 对象集中管理所有预定义错误，避免"散落各处的魔数"
- `MISSING_PARAMS` 是工厂函数，支持动态消息——`Errors.MISSING_PARAMS('用户名不能为空')`
- `Error.captureStackTrace` 确保错误堆栈干净，便于 debug

#### 测试：`tests/unit/errors.test.js`（6 条测试）

```javascript
// tests/unit/errors.test.js
/**
 * 错误类 — TDD 测试
 * Iter 1: 工具函数层
 */

const { AppError, Errors } = require('../../src/utils/errors');

describe('AppError', () => {
  it('应携带 message 和 statusCode', () => {
    const err = new AppError('自定义错误', 400);
    expect(err).toBeInstanceOf(Error);
    expect(err.message).toBe('自定义错误');
    expect(err.statusCode).toBe(400);
  });

  it('默认 statusCode 应为 500', () => {
    const err = new AppError('服务器错误');
    expect(err.statusCode).toBe(500);
  });

  it('应正确捕获堆栈', () => {
    const err = new AppError('测试');
    expect(err.stack).toBeDefined();
    expect(err.stack).toContain('AppError');
  });
});

describe('Errors 预定义错误', () => {
  it('INVALID_CREDENTIALS: 401 用户名或密码错误', () => {
    expect(Errors.INVALID_CREDENTIALS.statusCode).toBe(401);
    expect(Errors.INVALID_CREDENTIALS.message).toBe('用户名或密码错误');
  });

  it('MISSING_PARAMS: 工厂函数应生成动态消息', () => {
    const err = Errors.MISSING_PARAMS('用户名和密码不能为空');
    expect(err.statusCode).toBe(400);
    expect(err.message).toBe('用户名和密码不能为空');
  });

  it('INTERNAL: 500 服务器内部错误', () => {
    expect(Errors.INTERNAL.statusCode).toBe(500);
    expect(Errors.INTERNAL.message).toBe('服务器内部错误');
  });
});
```

**6 条测试覆盖了什么：**

| 测试 | 断言 |
|------|------|
| AppError 构造 | message + statusCode 正确赋值 |
| 默认 statusCode | 不传 statusCode = 500 |
| 堆栈捕获 | stack 存在且包含类名 |
| INVALID_CREDENTIALS | 401 + 固定消息 |
| MISSING_PARAMS | 400 + 动态消息 |
| INTERNAL | 500 + 固定消息 |

---

### 2.2 `src/utils/password.js` — 密码哈希与验证

```javascript
// src/utils/password.js
/**
 * 密码加密工具
 * Iter 1: 工具函数层（不依赖其他模块）
 */
const bcrypt = require('bcryptjs');

async function hashPassword(plainPassword) {
  if (!plainPassword || plainPassword.length < 6) {
    throw new Error('密码长度不能少于 6 位');
  }
  const salt = await bcrypt.genSalt(10);
  return bcrypt.hash(plainPassword, salt);
}

async function verifyPassword(plainPassword, hashedPassword) {
  return bcrypt.compare(plainPassword, hashedPassword);
}

module.exports = { hashPassword, verifyPassword };
```

**设计要点：**
- **边界检查**：`!plainPassword` 覆盖 `undefined`、`null`、空字符串
- **最小长度**：`length < 6` 拒绝短密码
- **明确 rounds**：`bcrypt.genSalt(10)` 有明确参数，不用默认值（默认值因版本而异）
- `verifyPassword` 是纯委托，直接调用 `bcrypt.compare`

#### 测试：`tests/unit/password.test.js`（4 条测试）

```javascript
// tests/unit/password.test.js
/**
 * 密码工具 — TDD 测试
 * Iter 1: 工具函数层
 */

const bcrypt = require('bcryptjs');
const { hashPassword, verifyPassword } = require('../../src/utils/password');

jest.mock('bcryptjs');

describe('password utils', () => {
  beforeEach(() => { jest.clearAllMocks(); });

  describe('hashPassword', () => {
    it('应返回哈希后的密码', async () => {
      bcrypt.genSalt.mockResolvedValue('fake-salt');
      bcrypt.hash.mockResolvedValue('hashed-password-123');
      const result = await hashPassword('mypassword123');
      expect(bcrypt.genSalt).toHaveBeenCalledWith(10);
      expect(bcrypt.hash).toHaveBeenCalledWith('mypassword123', 'fake-salt');
      expect(result).toBe('hashed-password-123');
    });

    it('密码少于 6 位时应抛出错误', async () => {
      await expect(hashPassword('12')).rejects.toThrow('密码长度不能少于 6 位');
    });
  });

  describe('verifyPassword', () => {
    it('密码匹配时应返回 true', async () => {
      bcrypt.compare.mockResolvedValue(true);
      const result = await verifyPassword('mypassword', 'hashed-value');
      expect(result).toBe(true);
    });

    it('密码不匹配时应返回 false', async () => {
      bcrypt.compare.mockResolvedValue(false);
      const result = await verifyPassword('wrongpass', 'hashed-value');
      expect(result).toBe(false);
    });
  });
});
```

**4 条测试覆盖了什么：**

| 测试 | 断言 |
|------|------|
| hashPassword 正常返回 | 调用 genSalt(10)，返回哈希值 |
| hashPassword 边界检查 | 短密码抛出异常 |
| verifyPassword 匹配 | 返回 true |
| verifyPassword 不匹配 | 返回 false |

注意这里使用了 `jest.mock('bcryptjs')` —— 因为真正的 bcrypt 哈希需要几十毫秒，而 mock 只需要几微秒。**测试速度很重要：跑得够快，你才愿意每次改代码都跑一遍。**

---

### 2.3 `src/utils/jwt.js` — JWT 令牌签发与验证

```javascript
// src/utils/jwt.js
/**
 * JWT 工具
 * Iter 1: 工具函数层（依赖 config）
 */
const jwt = require('jsonwebtoken');
const config = require('../config');

function signToken(userId) {
  return jwt.sign({ user_id: userId }, config.jwt.secret, { expiresIn: config.jwt.expiresIn });
}

function verifyToken(token) {
  return jwt.verify(token, config.jwt.secret);
}

module.exports = { signToken, verifyToken };
```

**设计要点：**
- **payload 格式约定**：使用 `{ user_id: userId }`，**不是** JWT 标准的 `sub`——这是 SPEC 明确规定的契约
- **secret 来自 config**：不硬编码，不写死在代码里
- **expiresIn 来自 config**：过期策略集中管理，改动不需要改代码

> JWT 的本质是**前后端的契约**。payload 里有什么字段、token 多久过期，这些不是代码决策，是**协议决策**。写在测试里，由机器自动校验。

#### 测试：`tests/unit/jwt.test.js`（3 条测试）

```javascript
// tests/unit/jwt.test.js
/**
 * JWT 工具 — TDD 测试
 * Iter 1: 工具函数层
 * payload 格式: { user_id, exp }
 */

const jwt = require('jsonwebtoken');
const config = require('../../src/config');
const { signToken, verifyToken } = require('../../src/utils/jwt');

jest.mock('jsonwebtoken');

describe('jwt utils', () => {
  beforeEach(() => { jest.clearAllMocks(); });

  describe('signToken', () => {
    it('签发 token 应使用 user_id', () => {
      jwt.sign.mockReturnValue('mock-token');
      const token = signToken(1);
      expect(jwt.sign).toHaveBeenCalledWith(
        { user_id: 1 },
        config.jwt.secret,
        { expiresIn: config.jwt.expiresIn }
      );
      expect(token).toBe('mock-token');
    });
  });

  describe('verifyToken', () => {
    it('有效 token 应返回 decoded payload', () => {
      const payload = { user_id: 1, exp: 9999999999 };
      jwt.verify.mockReturnValue(payload);
      const result = verifyToken('valid-token');
      expect(jwt.verify).toHaveBeenCalledWith('valid-token', config.jwt.secret);
      expect(result).toEqual(payload);
    });

    it('无效 token 应抛出异常', () => {
      jwt.verify.mockImplementation(() => { throw new Error('jwt malformed'); });
      expect(() => verifyToken('bad-token')).toThrow();
    });
  });
});
```

**3 条测试覆盖了什么：**

| 测试 | 断言 |
|------|------|
| signToken 格式 | payload = `{ user_id }`，使用 config 中的 secret 和 expiresIn |
| verifyToken 正常 | 正确调用 jwt.verify，返回 payload |
| verifyToken 异常 | 无效 token 抛出异常 |

---

### 2.4 TDD 红绿循环

Iter 1 的开发严格遵循 TDD 的红绿循环：

1. **RED**：先写测试 → 跑 → 失败（模块还不存在）
2. **GREEN**：写最少代码让测试通过
3. **REFACTOR**：优化代码，确保测试仍然通过

![](imgs/05/01-tdd-red-green-cycle.svg)

这种做法的核心价值在于：**每个文件的第一遍跑都是红色的，第二遍跑就绿了。** 这种"从红到绿的爽感"是 TDD 的天然正反馈——写测试的时候知道自己要什么，写代码的时候知道自己写对了，跑测试的时候知道自己真的写对了。

---

### 2.5 工具函数独立性

这三个文件有什么共同特点？

```
src/utils/errors.js    → 纯类定义，零依赖
src/utils/password.js  → 只依赖 bcryptjs（第三方库）
src/utils/jwt.js       → 依赖 jsonwebtoken + config
```

它们只依赖第三方库或 config 文件，**不依赖任何其他业务模块**。这意味着：

- 单元测试不需要启动服务器
- 单元测试不需要连接数据库
- 即使整个应用的其他部分都没写完，这三个文件已经可以独立测试

![](imgs/05/02-utils-independence.svg)

---

## 三、汇总：Iter 1 测试结果

```bash
$ npx jest tests/unit/errors.test.js tests/unit/password.test.js tests/unit/jwt.test.js

Test Suites: 3 passed, 3 total
Tests:       13 passed, 13 total
```

| 模块 | 测试条数 | 覆盖了什么 |
|------|---------|-----------|
| `errors.js` | 6 | 错误格式、默认 statusCode、堆栈、预定义错误常量 |
| `password.js` | 4 | 哈希返回、边界检查、匹配/不匹配验证 |
| `jwt.js` | 3 | payload 格式、config 使用、无效 token 异常 |

**13 条测试 = 13 个你不需要手动检查的点。**

Iter 1 做完，工具函数层稳了。下一步：**数据模型 + 种子数据。**

```
Tests: 13 passed, 13 total ✅
```

---

*下一篇：06-Iter 2——数据模型 + 种子数据。*