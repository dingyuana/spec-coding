# 把规范写成门禁——AGENT.md

---

## 一、为什么 AI 编码需要约束？

你让一个 AI 写一段登录功能。它唰唰唰写好了，测试也绿了。你正准备合并，仔细一看：

```javascript
// ❌ AI 可能写出的代码
const user = await db.query("select * from users where id = " + id);
ctx.body = { passwordHash: user.passwordHash };
```

两行代码，两个生产级漏洞。

**SQL 注入** —— `id` 是用户输入，直接拼进查询，一句 `' OR 1=1--` 就能把你的用户表全部 dump 出来。
**密码 Hash 泄露** —— 你把 `passwordHash` 原封不动怼进了响应体里，等于给所有注册用户的密文挂了张公示牌。

你深吸一口气，点了"Request Changes"。

然后你发现一个更绝望的事实：**这段代码 CI 是绿的。** ESLint 没报错。SonarQube 没报警。单元测试全过了。

![](imgs/03/01-three-layer-framework.svg)

### AI 编码的三大约束层次

在给 AI 编写规范时，需要理解三个层次：

| 层次 | 工具 | 检查内容 | 能拦住上面的漏洞吗？ |
|------|------|----------|---------------------|
| **语法层** | ESLint, Prettier | 分号、空格、未使用变量 | ❌ 语法完美，架构灾难 |
| **类型层** | TypeScript, Flow | 类型不匹配、null 引用 | ❌ 类型对了，语义可能全错 |
| **规范层** | AGENT.md（人肉可读） | 架构红线、安全约束、命名规范 | ✅ 告诉 AI 什么绝对不能做 |

**Linter 是语法门卫，不是架构门卫。**

再念一遍。**Linter 是语法门卫，不是架构门卫。**

ESLint 能管住你少了个分号、多了个空格、变量名不是 camelCase。**但它管不住 `select *`，管不住你把密码怼进响应里。** 它会告诉你"这里有个未使用的变量"——但不会告诉你"你正在把整个数据库的用户密码发给前端"。

这段代码在语法上是完美的。在架构上是灾难的。

![](imgs/03/02-linter-vs-agent-comparison.svg)

---

## 二、AI 编码规范的核心：命名 + 分层 + 红线

要让 AI 写出生产级代码，你需要给 AI 三样东西：

### 1. 命名规范——让代码自文档化

| 类型 | 风格 | 示例 | 原因 |
|------|------|------|------|
| 变量/函数 | camelCase | `findByUsername` | JS 惯例，与标准库一致 |
| 类 | PascalCase | `AppError` | 明确标识构造器 |
| 文件目录 | kebab-case | `authService.js` | 跨平台兼容，无大小写歧义 |

**反例**（AI 容易这样写）：`GetUserData_service.js`、`class user_data_handler` — 风格混搭、不可预测。

### 2. 分层规范——单向依赖，从上到下

```
config/  →  纯配置，不依赖项目内其他模块
utils/   →  纯工具函数，不依赖项目内其他模块
models/  →  数据存取，依赖 utils
services/ → 业务逻辑，依赖 models + utils
controllers/ → 参数校验 + 调用 service
routes/  →  路由映射
middleware/ → 跨切面逻辑
app.js + index.js → 组装
```

**核心原则：单向依赖，不允许反向引用。** service 不能 import controller，utils 不能 import models。这保证了每一层都可以独立测试、独立替换。

### 3. 禁止事项——红线清单

这不是那种"建议你用更好的方式"的软绵绵废话。这是门禁。每一条都是一道闸门。

| 禁止 | 原因 |
|------|------|
| 密码明文存储 | 必须 bcrypt，慢哈希，加盐 |
| JWT 密钥硬编码 | 必须从 `.env` 读取 |
| catch 后吞异常 | 必须 `throw` 或转 `AppError` |
| 登录泄露用户是否存在 | 防枚举攻击，错误消息必须完全一致 |
| 数据库查询不能拼接 SQL | 必须用参数化查询或 ORM |
| 敏感字段出现在响应体中 | 必须显式 `pick` 或 `omit` |

---

## 三、本项目的 AGENT.md

打开 `user-login/AGENT.md`（文件路径：`/root/spec-coding/AGENT.md`），完整内容如下：

```markdown
# 用户登录模块 — AGENT

## 命名规范
| 类型 | 风格 | 示例 |
|------|------|------|
| 变量/函数 | camelCase | findByUsername |
| 类 | PascalCase | AppError |
| 文件目录 | kebab-case | authService.js |

## 分层规范（单向依赖）
config/ → 纯配置
utils/  → 纯工具函数，不依赖项目内其他模块
models/ → 数据存取，依赖 utils
services/ → 业务逻辑，依赖 models + utils
controllers/ → 参数校验 + 调用 service
routes/ → 路由映射
middleware/ → 跨切面逻辑
app.js + index.js → 组装

## 禁止事项
| 禁止 | 原因 |
|------|------|
| 密码明文存储 | 必须 bcrypt |
| JWT 密钥硬编码 | 必须从 .env 读取 |
| catch 后吞异常 | 必须 throw 或转 AppError |
| 登录泄露用户是否存在 | 防枚举攻击 |

## 响应格式
**成功 (200):** `{ "token": "..." }`
**异常 (400/401/500):** `{ "error": "..." }`

## 开发迭代规范
1. 每个 Iter 先写测试（RED），再写代码（GREEN）
2. 一个 Iter 只新增 1-3 个文件
3. 上一个 Iter 全绿后才能进入下一个 Iter
```

**简洁、精确、无废话。** 没有"建议"这个词，全部是"必须"和"禁止"。

---

## 四、项目代码如何遵循 AGENT 规范

理论说完了。来看看本项目的实际代码如何逐条遵守 AGENT 规范。

### 示例一：命名规范 —— `src/utils/errors.js`

文件路径：`/root/spec-coding/src/utils/errors.js`

```javascript
/**
 * 自定义错误类
 * Iter 1: 工具函数层
 */
class AppError extends Error {                   // ✅ PascalCase — 类名
  constructor(message, statusCode = 500) {
    super(message);
    this.name = 'AppError';
    this.statusCode = statusCode;
    Error.captureStackTrace(this, this.constructor);
  }
}

const Errors = {
  INVALID_CREDENTIALS: new AppError('用户名或密码错误', 401),   // ✅ UPPER_SNAKE — 常量
  MISSING_PARAMS: (msg) => new AppError(msg, 400),            // ✅ UPPER_SNAKE — 工厂函数
  INTERNAL: new AppError('服务器内部错误', 500),                // ✅ UPPER_SNAKE — 常量
};

module.exports = { AppError, Errors };
```

**规范检查清单：**
- ✅ **camelCase**: `message`, `statusCode`, `Errors`
- ✅ **PascalCase**: `AppError`（类）
- ✅ **kebab-case**: 文件名 `errors.js`
- ✅ **文件位置**: `src/utils/errors.js` — 在 `utils/` 目录下，属于纯工具函数层

### 示例二：分层规范 —— `src/services/authService.js`

文件路径：`/root/spec-coding/src/services/authService.js`

```javascript
/**
 * 认证服务
 * Iter 3: 服务层
 * 依赖：UserModel, password, jwt
 */
const UserModel = require('../models/user');         // ✅ 依赖 models
const { verifyPassword } = require('../utils/password');  // ✅ 依赖 utils
const { signToken } = require('../utils/jwt');             // ✅ 依赖 utils
const { Errors } = require('../utils/errors');             // ✅ 依赖 utils

const AuthService = {
  async login({ username, password }) {
    const user = UserModel.findByUsername(username);       // ✅ 调用 models
    if (!user) throw Errors.INVALID_CREDENTIALS;           // ✅ 防枚举 — 用户不存在
    const isValid = await verifyPassword(password, user.passwordHash);
    if (!isValid) throw Errors.INVALID_CREDENTIALS;        // ✅ 防枚举 — 密码错误（同一错误）
    const token = signToken(user.id);                      // ✅ 调用 utils
    return { token };                                      // ✅ 返回格式 { token }
  },
};

module.exports = AuthService;
```

**单向依赖验证：**
```
src/services/authService.js
  ├── requires: ../models/user          ✅ models 层
  ├── requires: ../utils/password       ✅ utils 层
  ├── requires: ../utils/jwt            ✅ utils 层
  └── requires: ../utils/errors         ✅ utils 层
```
**没有反向引用** — 没有 import controller、没有 import routes。`services/` 只依赖它下面的层（models 和 utils），从不依赖上面的层。

### 示例三：禁止事项 —— 防枚举攻击

AGENT 说："登录不能泄露用户是否存在"。

在 `tests/integration/auth.test.js` 中：

```javascript
// AGENT 说：登录不能泄露用户是否存在
// 文件路径：tests/integration/auth.test.js
describe('Scenario 3: 用户不存在', () => {
  it('错误消息与密码错误完全一致（防枚举）', async () => {
    const [wrongPass, notFound] = await Promise.all([
      request(app.callback()).post('/api/auth/login')
        .send({ username: 'admin', password: 'wrong' }),
      request(app.callback()).post('/api/auth/login')
        .send({ username: 'ghost', password: 'x' }),
    ]);
    expect(wrongPass.body).toEqual(notFound.body);  // 完全一致，一个字都不能差
  });
});
```

### 示例四：禁止事项 —— 密码 bcrypt + 响应格式

AGENT 说："密码不能明文存储" + "响应格式为 { token }/{ error }"。

在 `src/controllers/authController.js` 中：

```javascript
/**
 * 认证控制器
 * Iter 4: HTTP 接口层
 */
const AuthService = require('../services/authService');  // ✅ 依赖 services
const { Errors } = require('../utils/errors');            // ✅ 依赖 utils

const AuthController = {
  async login(ctx) {
    const { username, password } = ctx.request.body;
    if (!username || !password)
      throw Errors.MISSING_PARAMS('用户名和密码不能为空');  // ✅ 400 格式
    const { token } = await AuthService.login({ username, password });
    ctx.status = 200;
    ctx.body = { token };  // ✅ 200 响应格式 { "token": "..." }
  },
};
```

**规范检查清单：**
- ✅ 密码通过 `AuthService` → `password.js` → `bcrypt` 处理，不存在明文
- ✅ 响应格式严格遵循 `{ token }`（200）和 `{ error }`（400/401/500）
- ✅ 不直接访问 model，而是通过 service 层

---

## 五、每一条 AGENT 规范，都有一条测试守卫

看见没？**AGENT 是一份人的约定，测试是一道代码的门禁。** 规范写进文件里，门禁写进测试里。人和机器一起守住一个标准。

| AGENT 规范 | 对应测试文件 | 测试内容 |
|------------|-------------|---------|
| 密码 bcrypt 存储 | `tests/unit/password.test.js` | hashPassword 返回 bcrypt 格式 |
| JWT 密钥从 .env 读 | `tests/unit/jwt.test.js` | 验证 signToken 使用 config.jwt.secret |
| 不泄露用户是否存在 | `tests/integration/auth.test.js` | 密码错误 vs 用户不存在返回相同 body |
| 参数校验 | `tests/integration/auth.test.js` | 缺失 username/password 返回 400 |
| 响应格式 | `tests/integration/auth.test.js` | 验证 resp.body.token 和 resp.body.error 结构 |

---

## 六、AI 编码最佳实践

总结一下如何在项目中给 AI 写规范，让 AI 生成"不用改就能上线"的代码：

1. **先写 AGENT.md，再让 AI 写代码** — 把规范作为 prompt 前缀注入
2. **每条规范都要有对应的测试** — 测试是最低级的验证，AGENT 是最高级的约束，两者缺一不可
3. **用禁止语气，不用建议语气** — "禁止"是能拦住人的，"建议"是被人忽略的
4. **让每条红线可测试** — 如果写不出测试来验证这条红线，说明它不够精确
5. **和 AI 协作时，先给 AGENT，再给任务** — 让 AI 在写代码前先理解约束

这是本项目 `AGENT.md` 只有 36 行的原因。**越精简的规范，越容易被遵守。** 没人会读一份 50 页的《编码规范手册》，但每个人都会扫一眼只有一页纸的门禁清单。

---

## 七、从规范到工程底座

规范写好了，红线画下了，门禁装上了。

但问题来了——你总不能让每个新来的同事自己去装依赖、配环境、建目录吧？

**你需要一个工程底座。** 一个放到哪都能跑的脚手架——`package.json` 写好依赖、`.env` 把密钥请进环境变量、`.gitignore` 把不该提交的东西拦在门外。

**下一篇**，我们就来搭这个底座——**一个连新人都不会跑偏的工程脚手架。**

---

*下一篇：04-脚手架——搭好工程底座。*