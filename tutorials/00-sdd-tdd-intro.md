# 从"会写代码"到"会设计代码"——SDD+TDD 框架

---

## 一、你肯定经历过这样的深夜

下午三点，你打开编辑器，心想："一个登录接口而已，开干。"

手指比脑子快。先写路由，再写控制器，顺手把数据库操作嵌在回调里。"先跑起来再说"，你对自己说。

六小时后——

1. 密码明文存进数据库了（哦对，忘了加密）
2. 加密了，但哈希也顺手返回给前端了（前端小哥甩来一个问号）
3. 修好了，然后发现同事在隔壁也写了个登录接口，返回字段名完全不一样
4. 产品经理飘来一句："加个字段吧。"
5. 改了，然后你发现——三个测试用例全挂了

等等，你写测试了？没有。你连测试文件都没建。

**你不孤独。每个从"能跑就行"走过来的开发者，都在这条路上摔过跤。**

问题不是你不努力。问题是你的流程错了。

---

## 二、"先写代码再说"——这条路上的三个坟头

这条路看起来最短，实际上绕得最远。

**第一座坟：设计只在你脑子里**

你的架构、你的分层、你的边界——全都是大脑中的瞬时记忆。代码是它唯一的物理表达。别人看不懂，三个月后的你同样看不懂。一个改动的影响范围？只能靠人肉回溯猜。

**第二座坟：不知道从哪开始**

12 个文件摊在面前：工具函数、模型、服务、控制器、路由、中间件、入口文件……你光标闪烁，不知道该写哪个。于是随便选一个埋头写，写到一半发现依赖还没建。

**第三座坟：改了不敢跑，跑了不敢改**

改了一处逻辑，心惊胆战。因为没测试，你不知道碰坏了什么。手动点一遍页面？今天是周四，那就周四下午留给回归测试——这不是开发，这是考古。

---

## 三、迭代式 SDD+TDD：一段从"摆摊"到"盖楼"的演进

先别急着写代码。我们来走一遍**思考的进化**。

### 阶段 1：最原始的本能——先写代码

> 打开编辑器 → 写路由 → 写逻辑 → 写数据库 → 跑起来 → 咦，好像少了个校验 → 回头补 → 啊，又改坏了什么地方

这是**摆摊式开发**：支个摊子就卖，下雨就收。没有蓝图，没有地基，今天能跑就是胜利。

### 阶段 2：稍微想一下——先写 README

> 写 README 描述这个模块做什么 → 然后写代码 → 做到一半发现 README 里漏了什么 → 改 README → 再写代码

比直接写代码好了一点点。**至少你知道自己要去哪。** 但 README 太模糊，它描述的是"想法"，不是"契约"。你和同事的理解可以完全不同。

### 阶段 3：真正的升级——先写 SPEC

> 写 SPEC 定义接口、输入、输出、边界 → 写测试验证这些契约 → 写代码实现 → 跑测试，全绿 ✅

这才是 **SDD（Spec-Driven Development）** 的精髓：**用 SPEC 把脑子里模糊的"想法"变成白纸黑字的"契约"；用 TDD（Test-Driven Development）把契约变成可执行的安全网。**

整个项目分 **5 个迭代**，每个迭代只做 2-3 个文件，每个文件先写测试再写代码。就像盖楼——打完地基再砌墙，砌完墙再布线，每一步都有验收标准。

---

## 四、项目实战：本项目真实结构

光讲理论不够。我们来看一个真实项目的文件树——这正是本教程配套的**用户登录模块**，一个基于 Koa + bcrypt + JWT 的完整认证系统。

```
user-login/                        ← 项目根目录
├── SPEC.md                        ← 全局契约（4 个 Scenario）
├── PLAN.md                        ← 迭代规划
├── AGENT.md                       ← 编码规范
├── package.json                   ← 项目配置
├── .env                           ← 环境变量
│
├── src/                           ← 源码目录
│   ├── config/index.js            ← 配置（.env 读取）
│   ├── utils/
│   │   ├── errors.js              ← AppError 类 + 预定义错误常量
│   │   ├── password.js            ← bcrypt 密码哈希/验证
│   │   └── jwt.js                 ← JWT 签发/验证
│   ├── models/user.js             ← User 模型（Map 存储）
│   ├── services/authService.js    ← 登录业务逻辑
│   ├── controllers/authController.js  ← 参数校验 + 格式化
│   ├── routes/auth.js             ← 路由映射
│   ├── middleware/errorHandler.js  ← 全局异常处理
│   ├── app.js                     ← 应用工厂
│   └── index.js                   ← 入口（含种子数据）
│
├── scripts/seed.js                ← 种子脚本
│
└── tests/                         ← 测试目录
    ├── unit/
    │   ├── errors.test.js         ← 6 条测试
    │   ├── password.test.js       ← 4 条测试
    │   ├── jwt.test.js            ← 3 条测试
    │   ├── userModel.test.js      ← 5 条测试
    │   └── authService.test.js    ← 3 条测试（mock）
    └── integration/
        └── auth.test.js           ← 8 条测试（4 个 Scenario）
```

注意这个结构——**每个文件的名字都暗示了它的职责**。你不打开代码，光看文件名就能猜出"错误处理在哪"、"密码怎么加密"、"路由怎么配的"。这就是设计的力量。

---

## 五、验证一下：真实的 package.json

```json
// package.json（scripts 部分）
{
  "scripts": {
    "start": "node src/index.js",
    "dev": "node --watch src/index.js",
    "test": "jest --verbose",
    "test:watch": "jest --watch"
  }
}
```

四个命令，清晰明了：

| 命令 | 用途 |
|------|------|
| `npm start` | 生产环境启动 |
| `npm run dev` | 开发模式（文件变化自动重启） |
| `npm test` | 跑全部测试，带详细输出 |
| `npm run test:watch` | 监听模式，改代码自动重跑 |

---

## 六、5 个迭代：从地基到封顶——每个 Iter 都标注了真实文件

这不是一个清单，这是一个项目从零到一的生长史。**每个迭代后面标注了该迭代产出的真实文件路径。**

---

### Iter 0：蓝图阶段（不写一行业务代码）

你在白板前站了一个小时。

你先写 **SPEC**——登录怎么做、注册要哪些字段、JWT 怎么签发、错误怎么返回。每一个接口的输入输出，白纸黑字写清楚。

然后写 **PLAN**——功能分成几步？依赖关系是什么？哪些先做、哪些后做？

接着写 **AGENT**（如果用 AI 辅助编码的话）——给 AI 明确的角色和约束。

最后搭 **脚手架**——项目结构、依赖安装、测试框架配置。**干净的地基，一堵墙都不砌。**

📄 **产出文件：**
- `SPEC.md` — 全局契约
- `PLAN.md` — 迭代规划
- `AGENT.md` — 编码规范
- `package.json` — 项目配置

---

### Iter 1：地基阶段——工具函数（3 个文件，13 条测试）

独立的 3 个文件，**不依赖任何其他模块，独立可测。**

先写测试，再写实现。每个文件跑通再进下一个。

#### 1.1 错误类

```javascript
// src/utils/errors.js — Iter 1
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

**对应的测试**（`tests/unit/errors.test.js`，6 条测试）：

```javascript
// tests/unit/errors.test.js — Iter 1, TDD RED
describe('AppError', () => {
  it('应携带 message 和 statusCode', () => { /* ... */ });
  it('默认 statusCode 应为 500', () => { /* ... */ });
  it('应正确捕获堆栈', () => { /* ... */ });
});

describe('Errors 预定义错误', () => {
  it('INVALID_CREDENTIALS: 401 用户名或密码错误', () => { /* ... */ });
  it('MISSING_PARAMS: 工厂函数应生成动态消息', () => { /* ... */ });
  it('INTERNAL: 500 服务器内部错误', () => { /* ... */ });
});
```

#### 1.2 密码工具

```javascript
// src/utils/password.js — Iter 1
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
```

**对应的测试**（`tests/unit/password.test.js`，4 条测试，mock bcrypt）。

#### 1.3 JWT 工具

```javascript
// src/utils/jwt.js — Iter 1
const jwt = require('jsonwebtoken');
const config = require('../config');

function signToken(userId) {
  return jwt.sign({ user_id: userId }, config.jwt.secret, { expiresIn: config.jwt.expiresIn });
}

function verifyToken(token) {
  return jwt.verify(token, config.jwt.secret);
}
```

**对应的测试**（`tests/unit/jwt.test.js`，3 条测试，mock jsonwebtoken）。

📄 **产出文件：** `src/utils/errors.js` + `src/utils/password.js` + `src/utils/jwt.js` + 13 条测试 ✅

---

### Iter 2：骨架阶段——数据模型（3 个文件）

#### 2.1 配置模块

```javascript
// src/config/index.js — Iter 2
const config = {
  port: parseInt(process.env.PORT, 10) || 3000,
  jwt: {
    secret: process.env.JWT_SECRET,
    expiresIn: parseInt(process.env.JWT_EXPIRES_IN, 10) || 86400,
  },
  bcrypt: {
    rounds: parseInt(process.env.BCRYPT_ROUNDS, 10) || 10,
  },
};
```

#### 2.2 User 模型

```javascript
// src/models/user.js — Iter 2
const users = new Map();
let nextId = 1;

const UserModel = {
  findByUsername(username) {
    return Array.from(users.values()).find((u) => u.username === username);
  },
  findById(id) { return users.get(id); },
  create({ username, passwordHash }) {
    const user = { id: nextId++, username, passwordHash, createdAt: new Date() };
    users.set(user.id, user);
    return user;
  },
  clear() { users.clear(); nextId = 1; },
};
```

**对应的测试**（`tests/unit/userModel.test.js`，5 条测试，覆盖 create / findByUsername / findById / clear）。

#### 2.3 种子脚本

```javascript
// scripts/seed.js — Iter 2
async function seedDatabase() {
  const existing = UserModel.findByUsername(SEED_USER.username);
  if (existing) return existing;  // 幂等性
  const passwordHash = await hashPassword(SEED_USER.password);
  return UserModel.create({ username: SEED_USER.username, passwordHash });
}
// 种子数据：admin / admin123
```

📄 **产出文件：** `src/config/index.js` + `src/models/user.js` + `scripts/seed.js`

---

### Iter 3：器官阶段——业务逻辑（1 个文件）

这是核心——登录业务逻辑。服务层不关心 HTTP 请求和响应，它只处理纯数据。**可单元测试、可替换、不耦合框架。**

```javascript
// src/services/authService.js — Iter 3
const AuthService = {
  async login({ username, password }) {
    const user = UserModel.findByUsername(username);
    if (!user) throw Errors.INVALID_CREDENTIALS;     // 用户不存在 → 401
    const isValid = await verifyPassword(password, user.passwordHash);
    if (!isValid) throw Errors.INVALID_CREDENTIALS;  // 密码错误 → 401（消息相同！防枚举）
    const token = signToken(user.id);
    return { token };
  },
};
```

注意第 4 行和第 6 行——**用户不存在和密码错误抛出的是同一个错误对象**。这意味着前端/攻击者无法区分"用户名不存在"和"密码错误"，这是安全设计。

**对应的测试**（`tests/unit/authService.test.js`，3 条测试，mock 了 UserModel / password / jwt）：

```javascript
// tests/unit/authService.test.js — Iter 3, TDD RED
// mock 三个依赖，只测业务逻辑

it('用户名密码正确应返回 token', async () => { /* ... */ });
it('密码错误应抛出 INVALID_CREDENTIALS', async () => { /* ... */ });
it('用户不存在应抛出 INVALID_CREDENTIALS', async () => { /* ... */ });
```

📄 **产出文件：** `src/services/authService.js` + 3 条测试 ✅

---

### Iter 4：表皮阶段——HTTP 接口（5 个文件）

把业务逻辑暴露给外部世界。**HTTP 层是最薄的一层。** 它只负责转换格式，不负责业务决策。

#### 4.1 全局错误处理

```javascript
// src/middleware/errorHandler.js — Iter 4
function errorHandler(err, ctx) {
  if (err instanceof AppError) {
    ctx.status = err.statusCode;
    ctx.body = { error: err.message };
    return;
  }
  ctx.status = 500;
  ctx.body = { error: '服务器内部错误' };
}
```

#### 4.2 控制器（参数校验）

```javascript
// src/controllers/authController.js — Iter 4
const AuthController = {
  async login(ctx) {
    const { username, password } = ctx.request.body;
    if (!username || !password) throw Errors.MISSING_PARAMS('用户名和密码不能为空');
    const { token } = await AuthService.login({ username, password });
    ctx.status = 200;
    ctx.body = { token };
  },
};
```

#### 4.3 路由映射

```javascript
// src/routes/auth.js — Iter 4
const router = new Router({ prefix: '/api/auth' });
router.post('/login', AuthController.login);
```

#### 4.4 应用组装

```javascript
// src/app.js — Iter 4
function createApp() {
  const app = new Koa();
  app.use(bodyParser());
  app.use(async (ctx, next) => {
    try { await next(); }
    catch (err) { errorHandler(err, ctx); }
  });
  app.use(authRouter.routes());
  return app;
}
```

#### 4.5 入口

```javascript
// src/index.js — Iter 4
async function main() {
  await seedDatabase();
  const app = createApp();
  app.listen(config.port, () => {
    console.log(`[server] http://localhost:${config.port}`);
  });
}
```

**集成测试**（`tests/integration/auth.test.js`，8 条测试，覆盖 4 个 Scenario）：

```javascript
// tests/integration/auth.test.js — Iter 4, TDD RED
// Scenario 1: 正常登录
it('admin 正确密码应返回 200 和 JWT token', async () => { /* ... */ });
it('JWT payload 应包含 user_id', async () => { /* ... */ });

// Scenario 2: 密码错误
it('应返回 401 和错误消息', async () => { /* ... */ });

// Scenario 3: 用户不存在
it('应返回 401', async () => { /* ... */ });
it('错误消息与密码错误完全一致（防枚举）', async () => { /* ... */ });

// Scenario 4: 参数缺失
it('缺少 username 应返回 400', async () => { /* ... */ });
it('缺少 password 应返回 400', async () => { /* ... */ });
it('两个字段都缺失应返回 400', async () => { /* ... */ });
```

📄 **产出文件：** `src/middleware/errorHandler.js` + `src/controllers/authController.js` + `src/routes/auth.js` + `src/app.js` + `src/index.js` + 8 条集成测试 ✅

---

### Iter 5：交付前夜——完整验证

```bash
$ npm test

> user-login@1.0.0 test
> jest --verbose

PASS tests/unit/errors.test.js
PASS tests/unit/password.test.js
PASS tests/unit/jwt.test.js
PASS tests/unit/userModel.test.js
PASS tests/unit/authService.test.js
PASS tests/integration/auth.test.js

Test Suites: 6 passed, 6 total
Tests:       30 passed, 30 total
Snapshots:   0 total
Time:        3.053 s
```

全部 30 条测试通过 ✅。不是大概能跑，**是有据可查地能跑。**

---

## 七、每个 Iter 内的节奏：RED → GREEN → ✅

每个迭代内部都遵循同样的节奏：

```text
① 读 SPEC，确定本次范围
② 写测试 —— 测试会失败（RED）
③ 写最少代码让它通过（GREEN）
④ 跑测试，全绿 ✅
⑤ 进入下一个 Iter
```

![](imgs/00/01-sdd-tdd-flowchart.svg)

**一次只面对 1-3 个文件的问题。** 出错的范围被锁死，改坏了立刻知道——不需要等全部写完再恐慌。

---

## 八、有规划和没规划——差距不是一点点

| 维度 | 你以前的做法（直觉式） | 用了 SDD+TDD 后 |
|:-----|:---------------------|:----------------|
| **起点** | 打开编辑器光标闪烁 | 打开 SPEC 明确契约 |

![](imgs/00/02-traditional-vs-sddtdd-comparison.svg)

| **写代码** | 12 个文件一起怼，写到哪算哪 | 每次 1-3 个文件，做完一个 Iter 再做下一个 |
| **测试** | "写完再测吧" → 忘了写 → 手动点页面 | 先写测试再写代码，30 条测试随时可跑 |
| **改需求** | 改了 1 处，不知道碰坏了哪 3 处，慌 | 跑测试，2 秒告诉你一切正常还是哪里碎了 |
| **重构** | 不敢动，除非产品经理拿刀架脖子上 | 放心改，有安全网兜底 |
| **新人接手** | 读代码猜意图，耗时 3 天 | 读 SPEC 理解契约，耗时 30 分钟 |
| **内心感受** | 每天都在修昨天的坑 | 每天都在搭明天的积木 |

**"先写代码再说"不是快，是把债借给了明天的自己。**

---

## 九、整个系列的路线图

```text
Iter 0 → SPEC / PLAN / AGENT        ← 📘 你在这里
Iter 1 → 工具函数（密码 + JWT + 错误）
Iter 2 → 数据模型 + 种子数据
Iter 3 → 服务层（登录业务逻辑）
Iter 4 → HTTP 接口（路由 + 控制器 + 中间件）
Iter 5 → 完整验证，30 条全绿 ✅
```

---

## 十、接下来的故事

现在你脑子里应该有一个画面了——不是"怎么写代码"，而是"怎么设计代码"。

但光有画面不够。**下一个问题才是最硬的骨头：怎么把产品经理那句"加个登录功能"翻译成一行行精确的接口契约？**

这就是 SPEC 要做的事。我们下一节见——带上你的白板笔。

---

*→ 继续阅读：[01-SPEC.md](./01-spec-tutorial.md) —— 把需求翻译成不可辩驳的契约*