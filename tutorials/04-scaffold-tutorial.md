# 04｜搭好工程底座——package.json + .env + .gitignore

## 40 分钟了，Hello World 在哪？

你刚从 GitHub 上 clone 了一个看起来很酷的项目。README 写了三行，最后一行是"欢迎贡献！"。

然后噩梦开始了。

入口在哪？`node index.js`？`npm start`？还是 `python app.py`？密钥去哪个文件填？`node_modules` 要不要提交？

你翻遍了 Issues、Wiki、Google 缓存，甚至去 Discord 里翻了两百条历史消息。

**40 分钟过去了，你还没看到一句 Hello World。**

这不是你的问题。这是项目没有"工程底座"的问题。

---

## 三个文件，就像房子的水电煤

你搬进一套新房子，第一件事是确认三样东西：**电（入口）、水（配置）、煤气（安全）**。缺一个，这房子就住不了人。

一个工程项目的底座，也是三个文件：

| 文件 | 比喻 | 一句话职责 |
|------|------|-----------|
| `package.json` | **电闸** | 统一入口，告诉新人怎么开怎么关 |
| `.env` | **水表** | 配置分离，密钥不进代码 |
| `.gitignore` | **煤气安全阀** | 自动挡停，不该提交的别提交 |

![](imgs/04/01-three-files-infographic.svg)

缺一个，新人就得多花 40 分钟。三个都齐了，人家只需要一句话：

```bash
npm install && npm run dev
```

下面我们一个一个拆。

---

## 一、package.json——电闸，统一入口

### 血泪教训

我见过一个项目，启动方式写在 Confluence 的隐藏页面里，那个页面三个月前被删了。新来的同事花了两个下午才从 CI 日志里反推出启动命令。

更离谱的是，有人把 `npm start` 和 `npm run dev` 混用，结果 `start` 跑的是生产模式，`dev` 跑的是开发模式，新人用 `npm start` 启动开发，改代码不热更新，以为是框架有问题，debug 了一整天。

**一个没有 `package.json` 脚本规范的项目，就是一座没有电闸的房子——你要在黑暗中摸墙找开关。**

### 怎么做

```json
{
  "name": "my-awesome-project",
  "version": "1.0.0",
  "scripts": {
    "start": "node src/index.js",
    "dev": "node --watch src/index.js",
    "test": "jest --verbose",
    "lint": "eslint src/"
  },
  "dependencies": {
    "koa": "^2.15.3",
    "bcryptjs": "^2.4.3",
    "jsonwebtoken": "^9.0.2"
  }
}
```

**关键原则：**

- **`scripts` 是第一优先级**——任何启动、测试、lint 操作，统一走 `npm run <script>`。禁止新人去猜 `node` 还是 `nodemon` 还是 `ts-node`。
- **`dev` 和 `start` 分开**——`dev` 带 watch（开发热更新），`start` 是生产入口。新人一律 `npm run dev`。
- **依赖版本锁定用 `^` 还是 `~` 还是 `exact`？** 对于库项目用 `^`（兼容性更好），对于应用项目建议 lockfile + `^` 即可，不要纠结。

**效果：新人不需要知道你的项目用 Koa 还是 Express，不需要知道 Node 版本号，不需要翻 README 找启动命令。** 一个 `npm run dev` 搞定。

---

## 二、.env——水表，配置与代码分离

### 血泪教训

2017 年，一个叫 Alex 的工程师把生产环境的 AWS 密钥写在了 `config.js` 里，提交到了 GitHub 公开仓库。15 分钟后，有人用他的密钥跑了 4000 美元的计算实例。

这不是段子，每隔几天 GitHub 上就会有人把 `.env` 提交上去。**密钥散步到全世界，只需要一次 `git push`。**

还有一种更隐蔽的痛：你接手了一个项目，`config.js` 里写死了 `JWT_SECRET: 'abc123'`。你想改，但不知道哪些地方引用了它。你搜了全局，发现有人用 `process.env.JWT_SECRET`，有人用 `require('./config').jwtSecret`，有人直接硬编码在路由文件里。一份配置，三种写法，改一个崩三个。

**配置不分离的后果，是密钥永远在泄露的边缘试探，而改配置永远像拆炸弹。**

### 怎么做

```ini
# .env 文件（被 .gitignore，不上传仓库）
JWT_SECRET=dev-secret-key-change-in-production
JWT_EXPIRES_IN=86400
BCRYPT_ROUNDS=10
DATABASE_URL=postgres://localhost:5432/myapp
```

同时创建一个 `**`.env.example``**（上仓库，供参考）：

```ini
# .env.example（上仓库，给新人看的模板）
JWT_SECRET=your-secret-here
JWT_EXPIRES_IN=86400
BCRYPT_ROUNDS=10
DATABASE_URL=postgres://user:password@host:port/dbname
```

**关键原则：**

- **`.env` 永远在 `.gitignore` 里**——这是底线。漏了就是安全事故。
- **`.env.example` 必须进仓库**——新人 clone 后第一件事：`cp .env.example .env`，然后填自己的值。
- **代码里统一用 `process.env.XXX` 读取**——不要混合 `config.js` 和 `process.env`。统一入口，统一读取。
- **`.env` 只放非敏感默认值**——生产环境的真实密钥通过 CI/CD 环境变量注入，不要写在任何文件中。

**效果：新人 clone 项目后，不需要问"密钥从哪来"。** `.env.example` 就是说明书，`cp` 一下，填自己的值，搞定。

---

## 三、.gitignore——煤气安全阀，自动挡停

### 血泪教训

我见过一个项目，`node_modules` 被提交了。700MB 的二进制文件，每次 `git pull` 都要等 3 分钟。更可怕的是，里面有个依赖包被植入了恶意代码，团队毫无察觉，因为没人会去 review `node_modules` 里的内容。

另一个故事：一个实习生把 `.env` 提交了，项目经理发现后让他删掉重新 push。但 git 的历史里还有。**密钥一旦进了 git 历史，就永远在那里了。** 解决方法是 `git filter-branch` 重写历史，或者直接换密钥——后者比前者简单一百倍。

**`.gitignore` 不是一个建议，是一个自动挡停装置。** 它不考验人的记忆力，不用靠"提交前再检查一遍"这种会失效的流程。

### 怎么做

```gitignore
# .gitignore

# 依赖 - 不提交，永远 npm install
node_modules/

# 配置 - 不提交，永远 cp .env.example .env
.env
.env.local
.env.production

# 系统文件 - 不提交，没人关心
.DS_Store
Thumbs.db

# 日志 - 不提交，每人电脑上的日志都不一样
logs/
*.log
npm-debug.log*

# 构建产物 - 不提交，CI/CD 会重新构建
dist/
build/
*.tsbuildinfo
```

**关键原则：**

- **`node_modules/` 是第一条**——漏了就是 700MB 的噩梦。
- **`.env` 是第二条**——漏了就是安全事故。
- **每次新增一个工具/框架，第一时间把它的产物加到 `.gitignore` 里**——`next build` 产出 `.next/`，`tsc` 产出 `dist/`，`pnpm` 产出 `.pnpm-store/`。
- **用 `git status` 养成习惯**——`commit` 之前看一眼，确认没有意外文件。

**效果：新人不需要记住"哪些文件不能提交"。** `.gitignore` 替他们挡死了。想犯错都犯不了。

---

## 有底座 vs 没底座，差距有多大？

| 场景 | 没底座（40 分钟 + 安全隐患） | 有底座（5 分钟 + 安心） |
|------|---------------------------|----------------------|

![](imgs/04/02-cognitive-friction-comparison.svg)

| 新人启动项目 | 翻文档、搜 Issues、猜命令、问同事 …… 40 分钟 | `npm install && npm run dev`，一句搞定 |
| 配置密钥 | 改 `config.js`，提心吊胆怕提交 | `cp .env.example .env`，填自己的值 |
| 提交代码 | 反复检查"我有没有提交 .env？" | `.gitignore` 自动挡停，想犯错都难 |
| 换人维护 | 下一个接手的人重新经历一遍你的痛苦 | 无缝切换，零认知负担 |

**三个文件，加起来不到 30 行。** 但它们决定了你的项目是"clone 后 5 分钟上手"还是"clone 后 40 分钟还在找开关"。

---

## 进入 Iter 1

工程底座搭好了——电闸有了（package.json），水表有了（.env），煤气安全阀有了（.gitignore）。

现在这座房子可以住人了。

**下一篇：Iter 1——工具函数层（errors + password + jwt）。** 我们开始写真正的代码。