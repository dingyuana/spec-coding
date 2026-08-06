# 从"会写代码"到"会设计代码"——SDD+TDD 框架

---

## 一、引言

在现代软件开发中，需求变更频繁、系统复杂度持续增长，如何保证代码质量和可维护性成为每个团队的必修课。**SDD（Specification-Driven Development，规格驱动开发）** 与 **TDD（Test-Driven Development，测试驱动开发）** 是两种主流的开发方法论。将二者结合，可以在项目初期明确边界、在开发过程中持续验证，形成"先定义规格，再编写测试，最后实现代码"的高质量开发闭环。

本文不仅讲解 SDD+TDD 的理论，更会**带你走进一个真实项目**——一个基于 Koa + bcrypt + JWT 的用户登录模块。理论讲完，立刻看实际代码，每一步都有据可查。

---

## 二、基础概念

### 2.1 什么是 SDD（规格驱动开发）

SDD 是一种**从规格文档出发**的开发方法。在编写任何代码之前，团队先产出明确的功能规格说明书，定义输入、输出、边界条件、异常情况等。规格是「单一真相来源」（Single Source of Truth），后续的设计、编码、测试都围绕它展开。

SDD 的核心原则：

- **先定义再实现**：不写没有规格的代码
- **规格即契约**：任何变更都必须先更新规格
- **可验证性**：规格必须具备可测试性，模棱两可的描述不被接受

### 2.2 什么是 TDD（测试驱动开发）

TDD 由 Kent Beck 提出，遵循 **红 → 绿 → 重构** 的循环节奏：

1. **红（Red）**：先写一个会失败的测试用例
2. **绿（Green）**：编写刚好让测试通过的最简代码
3. **重构（Refactor）**：在测试保护下优化代码结构

TDD 的核心价值在于让测试成为代码的「安全网」，每一次修改都有自动化验证，从而敢于频繁重构、持续交付。

### 2.3 为什么要结合 SDD 和 TDD

| 维度 | SDD | TDD |
|------|-----|-----|
| 关注点 | 做什么（What） | 怎么做（How） |
| 产出物 | 规格文档 / API 契约 | 测试用例 / 实现代码 |
| 验证层面 | 需求正确性 | 实现正确性 |
| 编写时机 | 开发前 | 开发中 |

单独使用 SDD，容易产出"规格完美但实现偏离"的代码；单独使用 TDD，容易陷入"测试驱动但需求不清"的困境。将二者结合，**SDD 定义方向，TDD 保证执行**，形成从需求到代码的完整追溯链。

---

## 三、SDD + TDD 结合工作流

完整的开发流程分为以下五个阶段：

### 3.1 阶段一：书写规格文档

以功能模块为单位，撰写结构化规格说明。一个好的规格文档应包含：

- **功能描述**：一句话概括该功能的目标
- **输入参数**：类型、必填/可选、取值范围
- **输出结果**：成功时的返回结构、错误时的异常信息
- **边界条件**：空值、极限值、并发场景
- **业务规则**：核心计算逻辑、状态流转规则

### 3.2 阶段二：规格评审

规格文档完成后，由产品经理、开发工程师、测试工程师共同评审，确认：

- 需求理解一致，无歧义
- 边界条件覆盖完整
- 异常处理策略明确

评审通过后，**规格即冻结**，后续变更需走正式的变更流程。

### 3.3 阶段三：编写测试（TDD-Red）

基于冻结的规格，编写测试用例。这个阶段**不写实现代码**，所有测试必须失败（红色）。

### 3.4 阶段四：实现代码（TDD-Green）

编写刚好能让测试通过的最简实现，不做过度设计。

### 3.5 阶段五：重构优化（TDD-Refactor）

测试全部通过后，在绿色状态下对代码进行重构：

- 提取常量，消除魔法值
- 拆分过大的方法
- 优化异常处理层次
- 提升可读性

**每个迭代内部都遵循这个节奏：**

```text
① 读 SPEC，确定本次范围
② 写测试 —— 测试会失败（RED）
③ 写最少代码让它通过（GREEN）
④ 跑测试，全绿 ✅
⑤ 进入下一个 Iter
```

![](imgs/00/01-sdd-tdd-flowchart.svg)

---

## 四、项目实战：用户登录模块

光讲理论不够。我们来看一个真实项目——这正是本教程配套的**用户登录模块**，一个基于 Koa + bcrypt + JWT 的完整认证系统。

### 4.1 项目结构

```text
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

### 4.2 脚手架配置

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

| 命令 | 用途 |
|------|------|
| `npm start` | 生产环境启动 |
| `npm run dev` | 开发模式（文件变化自动重启） |
| `npm test` | 跑全部测试，带详细输出 |
| `npm run test:watch` | 监听模式，改代码自动重跑 |

### 4.3 5 个迭代：从地基到封顶

这不是一个清单，这是一个项目从零到一的生长史。**每个迭代后面标注了该迭代产出的真实文件路径。**

---

#### Iter 0：蓝图阶段（不写一行业务代码）

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

#### Iter 1：地基阶段——工具函数（3 个文件，13 条测试）

独立的 3 个文件，**不依赖任何其他模块，独立可测。**

**1.1 错误类**

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

**1.2 密码工具**

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

**1.3 JWT 工具**

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

#### Iter 2：骨架阶段——数据模型（3 个文件）

**2.1 配置模块**

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

**2.2 User 模型**

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

**2.3 种子脚本**

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

#### Iter 3：器官阶段——业务逻辑（1 个文件）

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

#### Iter 4：表皮阶段——HTTP 接口（5 个文件）

把业务逻辑暴露给外部世界。**HTTP 层是最薄的一层。** 它只负责转换格式，不负责业务决策。

**4.1 全局错误处理**

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

**4.2 控制器（参数校验）**

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

**4.3 路由映射**

```javascript
// src/routes/auth.js — Iter 4
const router = new Router({ prefix: '/api/auth' });
router.post('/login', AuthController.login);
```

**4.4 应用组装**

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

**4.5 入口**

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

#### Iter 5：交付前夜——完整验证

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

### 4.4 有规划和没规划——差距不是一点点

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

## 五、SDD 与 TDD 的协同优势

### 5.1 需求追溯能力

从生产环境的问题，可以溯源到规格文档、测试用例和实现代码，形成完整链路：

```
BUG → 对应测试用例 → 对应规格条目 → 需求来源
```

在本项目中，这条链路清晰可见：`SPEC.md` 的 Scenario 2（密码错误）→ `tests/integration/auth.test.js`（对应测试）→ `src/services/authService.js`（实现代码）→ `AGENT.md`（规范约束）。**三层约束，层层锁定。**

### 5.2 减少返工

传统开发中，大量返工源于"理解不一致"。SDD 在编码前就锁定了规格，TDD 让验收标准自动化，两者结合将返工率降低 50% 以上。本项目从 Iter 0 到 Iter 5，**没有一次因为"需求理解错了"而返工**——因为 SPEC 在写第一行代码之前就已经和需求对齐了。

### 5.3 文档即测试，测试即文档

规格文档直接映射测试用例，测试代码本身也是可执行的规格说明。新人接手模块时，阅读测试代码就能理解业务规则，降低沟通成本。

在本项目中，`tests/integration/auth.test.js` 的 8 条测试直接对应 SPEC.md 的 4 个 Scenario——测试的 describe 块名就是 Scenario 名，测试的 it 描述就是业务规则。**测试就是活的文档。**

---

## 六、适用场景与注意事项

### 6.1 推荐使用场景

- **后端 API 开发**：输入输出明确，天然适合 SDD 规格化
- **金融 / 医疗系统**：对正确性要求极高，需要完整追溯
- **多人协作模块**：规格作为团队共识基础
- **微服务边界**：服务间契约必须先行定义

### 6.2 注意事项

1. **不要过度规格化**：UI 交互、动画效果等难以结构化描述的领域，适度放松规格粒度
2. **规格维护成本**：规格文档本身也是代码资产，需要随需求演进持续维护
3. **测试覆盖不是 100%**：聚焦核心业务逻辑和边界条件，避免为测而测
4. **团队共识先行**：SDD+TDD 需要全员认同，强制推行效果甚微

---

## 七、总结

SDD 回答了"我们要构建什么"，TDD 回答了"我们构建的是正确的东西吗"。二者结合，从需求源头到代码交付形成闭环，兼顾了**需求正确性**与**实现正确性**。

在实践 SDD+TDD 时，记住这个简单口诀：

> **规格写清楚，测试先跑红，代码刚刚好，重构不能少。**

当你开始用这种方式开发，你会发现 Bug 变少了、重构变大胆了、代码审查变轻松了——因为这些质量保障机制，从代码的第一行就已经开始运转。

---

## 八、整个系列的路线图

```text
Iter 0 → SPEC / PLAN / AGENT        ← 📘 你在这里
Iter 1 → 工具函数（密码 + JWT + 错误）  
Iter 2 → 数据模型 + 种子数据  
Iter 3 → 服务层（登录业务逻辑）  
Iter 4 → HTTP 接口（路由 + 控制器 + 中间件）  
Iter 5 → 完整验证，30 条全绿 ✅
```

---

*→ 继续阅读：[01-SPEC.md](./01-SPEC.md) —— 把需求翻译成不可辩驳的契约*