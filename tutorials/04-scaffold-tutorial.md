# 04｜搭好工程底座——package.json + .env + .gitignore

---

## 40 分钟了，Hello World 在哪？

你刚从 GitHub 上 clone 了一个看起来很酷的项目。README 写了三行，最后一行是"欢迎贡献！"。

然后噩梦开始了。

入口在哪？`node index.js`？`npm start`？还是 `python app.py`？密钥去哪个文件填？`node_modules` 要不要提交？

你翻遍了 Issues、Wiki、Google 缓存，甚至去 Discord 里翻了两百条历史消息。

**40 分钟过去了，你还没看到一句 Hello World。**

这不是你的问题。这是项目没有"工程底座"的问题。

---

## 脚手架三要素：入口 / 配置 / 安全

一个工程项目的底座，由三个文件构成，分别对应三个维度：

| 维度 | 文件 | 要解决的问题 | 类比 |
|------|------|-------------|------|
| **入口 (Entry)** | `package.json` | 新人不知道项目怎么启动、怎么测试 | 电闸 — 统一入口，告诉新人怎么开怎么关 |
| **配置 (Config)** | `.env` | 密钥硬编码、配置与代码混在一起 | 水表 — 配置分离，密钥不进代码 |
| **安全 (Security)** | `.gitignore` | 不该提交的文件被 push 上仓库 | 煤气安全阀 — 自动挡停，不该提交的别提交 |

> **缺一个，新人就得多花 40 分钟。三个都齐了，人家只需要一句话：**
>
> ```bash
> npm install && npm run dev
> ```

![](imgs/04/01-three-files-infographic.svg)

下面我们一个一个拆。

---

## 一、package.json——电闸，统一入口

### 理论：为什么入口重要？

一个项目可能有多个启动方式——开发模式、生产模式、测试模式、lint、build。如果这些命令散落在 README、Wiki、Confluence 甚至同事的聊天记录里，每个新人都要经历"找入口"的痛苦。

**`package.json` 的 `scripts` 字段就是唯一的入口。** 所有操作统一走 `npm run <script>`，禁止猜命令。

### 本项目的 package.json

文件路径：`/root/spec-coding/package.json`

```json
{
  "name": "user-login",
  "version": "1.0.0",
  "description": "SDD+TDD 实战：用户登录模块 — Koa + bcrypt + JWT",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "node --watch src/index.js",
    "test": "jest --verbose",
    "test:watch": "jest --watch"
  },
  "devDependencies": {
    "jest": "^29.7.0",
    "supertest": "^7.0.0"
  },
  "dependencies": {
    "bcryptjs": "^2.4.3",
    "dotenv": "^16.4.5",
    "jsonwebtoken": "^9.0.2",
    "koa": "^2.15.3",
    "koa-bodyparser": "^4.4.1",
    "koa-router": "^12.0.1"
  }
}
```

### 关键原则详解

**1. `scripts` 是第一优先级**

本项目定义了 4 个脚本：

| 脚本 | 命令 | 用途 |
|------|------|------|
| `start` | `node src/index.js` | 生产入口 |
| `dev` | `node --watch src/index.js` | 开发模式（热更新） |
| `test` | `jest --verbose` | 运行全部测试（详细输出） |
| `test:watch` | `jest --watch` | 监听模式运行测试 |

新人只需要知道一个命令：`npm run dev`。不需要知道 `node` vs `nodemon` vs `ts-node`，不需要知道 `--watch` 参数。

**2. `dev` 和 `start` 分开**

- `dev` 带 `--watch`：开发时自动重启，改代码即时生效
- `start` 不带 watch：生产环境用，稳定可靠

**效果：** 新人 clone 项目后，不需要问"我怎么启动"——`npm run dev` 就是答案。

**3. 依赖分层清晰**

- **`dependencies`**（运行时依赖）：`koa`（Web 框架）、`bcryptjs`（密码哈希）、`jsonwebtoken`（JWT）、`dotenv`（环境变量）、`koa-bodyparser`（请求体解析）、`koa-router`（路由）
- **`devDependencies`**（开发时依赖）：`jest`（测试框架）、`supertest`（HTTP 测试）

每层各司其职，没有不必要的包混入。

**4. `main` 指向入口**

`"main": "src/index.js"` — 告诉所有人这个项目的入口文件在哪。不需要翻目录结构去找。

---

## 二、.env——水表，配置与代码分离

### 理论：为什么要把配置从代码里分离出去？

2017 年，一个叫 Alex 的工程师把生产环境的 AWS 密钥写在了 `config.js` 里，提交到了 GitHub 公开仓库。15 分钟后，有人用他的密钥跑了 4000 美元的计算实例。

这不是段子。每隔几天 GitHub 上就会有人把 `.env` 提交上去。**密钥散步到全世界，只需要一次 `git push`。**

还有一种更隐蔽的痛：你接手了一个项目，`config.js` 里写死了 `JWT_SECRET: 'abc123'`。你想改，但不知道哪些地方引用了它。你搜了全局，发现有人用 `process.env.JWT_SECRET`，有人用 `require('./config').jwtSecret`，有人直接硬编码在路由文件里。一份配置，三种写法，改一个崩三个。

**配置不分离的后果，是密钥永远在泄露的边缘试探，而改配置永远像拆炸弹。**

### 本项目的 .env.example

文件路径：`/root/spec-coding/.env.example`

```ini
# 服务端口
PORT=3000

# JWT 密钥（生成强随机字符串：openssl rand -hex 64）
JWT_SECRET=your-super-secret-key-change-in-production

# JWT 过期时间（秒）— 默认 24 小时
JWT_EXPIRES_IN=86400

# 密码哈希轮数（默认 10）
BCRYPT_ROUNDS=10
```

### 本项目的 .env

文件路径：`/root/spec-coding/.env`（被 `.gitignore` 保护，不上传仓库）

```ini
PORT=3000
JWT_SECRET=dev-secret-key-change-in-production
JWT_EXPIRES_IN=86400
BCRYPT_ROUNDS=10
```

### 代码如何读取配置

文件路径：`/root/spec-coding/src/config/index.js`

```javascript
/**
 * 配置
 * Iter 2: 数据模型
 */
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(__dirname, '../../.env') });

const config = {
  port: parseInt(process.env.PORT, 10) || 3000,
  jwt: {
    secret: process.env.JWT_SECRET,                                   // ✅ 从 .env 读取
    expiresIn: parseInt(process.env.JWT_EXPIRES_IN, 10) || 86400,
  },
  bcrypt: {
    rounds: parseInt(process.env.BCRYPT_ROUNDS, 10) || 10,
  },
};

if (!config.jwt.secret) {
  console.error('[FATAL] JWT_SECRET 未设置');                          // ✅ 启动时校验
  process.exit(1);
}

module.exports = config;
```

### 关键原则

- **`.env` 永远在 `.gitignore` 里**——这是底线。漏了就是安全事故。本项目的 `.env` 被明确排除。
- **`.env.example` 必须进仓库**——新人 clone 后第一件事：`cp .env.example .env`，然后填自己的值。
- **代码里统一用 `process.env.XXX` 读取**——通过 `src/config/index.js` 作为唯一入口，不混合 `config.js` 和 `process.env`。
- **启动时校验**——`if (!config.jwt.secret) process.exit(1)` — 如果密钥没配，项目直接拒绝启动，而不是运行时报奇怪的错。
- **注释指引**——`.env.example` 里写了生成 JWT 密钥的命令：`openssl rand -hex 64`。新人不用去搜"怎么生成 JWT 密钥"。

**效果：新人 clone 项目后，不需要问"密钥从哪来"。** `.env.example` 就是说明书，`cp` 一下，填自己的值，搞定。

---

## 三、.gitignore——煤气安全阀，自动挡停

### 理论：为什么需要 `.gitignore`？

`.gitignore` 不是一个建议，是一个**自动挡停装置**。它不考验人的记忆力，不用靠"提交前再检查一遍"这种会失效的流程。

**每次新增一个工具/框架，第一时间把它的产物加到 `.gitignore` 里。** 忘了加，就是在给下一个踩坑的人铺路。

常见该忽略的文件类型：

| 类型 | 示例 | 忽略原因 |
|------|------|---------|
| 依赖目录 | `node_modules/` | 700MB+，每次 clone 都要下载 |
| 配置文件 | `.env` | 包含密钥，泄露=安全事故 |
| 系统文件 | `.DS_Store`, `Thumbs.db` | 对项目无意义 |
| 日志 | `*.log`, `npm-debug.log*` | 每台机器不同 |
| 构建产物 | `dist/`, `build/` | CI/CD 会重新构建 |

### 本项目的 .gitignore

文件路径：`/root/spec-coding/.gitignore`

```gitignore
node_modules/
.env
npm-debug.log*
yarn-error.log*
```

看似简单，但已经涵盖了三个最核心的风险区域：

1. **`node_modules/`** — 700MB 的依赖目录，绝不能提交。漏了就是每次 `git pull` 等 3 分钟。
2. **`.env`** — 密钥文件，绝不能提交。漏了就是安全事故——一旦进了 git 历史，`git filter-branch` 重写历史或者直接换密钥。
3. **`npm-debug.log*` / `yarn-error.log*`** — 调试日志，包含本地路径和环境信息，不应进入仓库。

---

## 有底座 vs 没底座，差距有多大？

| 场景 | 没底座（40 分钟 + 安全隐患） | 有底座（5 分钟 + 安心） |
|------|---------------------------|----------------------|
| **新人启动项目** | 翻文档、搜 Issues、猜命令、问同事 …… 40 分钟 | `npm install && npm run dev`，一句搞定 |
| **配置密钥** | 改 `config.js`，提心吊胆怕提交 | `cp .env.example .env`，填自己的值 |
| **提交代码** | 反复检查"我有没有提交 .env？" | `.gitignore` 自动挡停，想犯错都难 |
| **换人维护** | 下一个接手的人重新经历一遍你的痛苦 | 无缝切换，零认知负担 |
| **密钥泄露** | GitHub 公开仓库 + 4000 美元账单 | `.env` 被 `.gitignore` 拦死，永远进不了仓库 |

![](imgs/04/02-cognitive-friction-comparison.svg)

**三个文件，加起来不到 30 行。** 但它们决定了你的项目是"clone 后 5 分钟上手"还是"clone 后 40 分钟还在找开关"。

---

## 进入 Iter 1

工程底座搭好了——电闸有了（package.json），水表有了（.env），煤气安全阀有了（.gitignore）。

现在这座房子可以住人了。

**下一篇：Iter 1——工具函数层（errors + password + jwt）。** 我们开始写真正的代码。