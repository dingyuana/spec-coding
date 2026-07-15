# 搭好工程底座——package.json + .env + .gitignore

> **场景带入 → 发现问题 → 方案迭代 → 原理拆解 → 效果对比 → 情绪升华**

---

## 一、你肯定遇到过的问题

你 clone 了一个新项目，打开 README——写着"欢迎贡献！"。

然后你开始猜：怎么启动？`node index.js`？`npm start`？装完依赖发现 `.env` 不存在，密钥从哪来？`node_modules` 要不要提交？

**40 分钟过去了，你还没看到一句 Hello World。**

## 二、最直接的做法：缺什么补什么

有人把密钥写死在 config.js 里、有人把 node_modules 提交了、有人把 .env 提交了——**密钥散步到了全世界。**

## 三、所以换一种思路：三个文件，各司其职

### package.json——统一入口

```json
{
  "scripts": {
    "start": "node src/index.js",
    "dev": "node --watch src/index.js",
    "test": "jest --verbose"
  },
  "dependencies": {
    "koa": "^2.15.3",
    "bcryptjs": "^2.4.3",
    "jsonwebtoken": "^9.0.2"
  }
}
```

**新人不需要猜命令：** `npm run dev` 启动，`npm test` 跑测试。

### .env——配置与代码分离

```ini
JWT_SECRET=dev-secret-key-change-in-production
JWT_EXPIRES_IN=86400    # 24 小时
BCRYPT_ROUNDS=10
```

密钥不写在代码里，从环境变量读取。还有 `.env.example` 作为模板。

### .gitignore——自动防线

![](imgs/04/01-three-files-infographic.svg)

```
node_modules/    # 依赖包不提交
.env             # 密钥不提交
```

两行，堵住两个最常见的安全事故。

## 四、本质：让新人零认知负担

没有脚手架，新人需要知道的暗知识：

```
启动用 node 还是 nodemon 还是 npm script？  ← package.json 解决
密钥写在哪？config.js 还是 .env？            ← .env 解决
node_modules 要不要提交？                     ← .gitignore 解决
```

有脚手架，新人只需要知道一件事：

![](imgs/04/02-cognitive-friction-comparison.svg)

```bash
npm install && npm run dev
```

## 五、有脚手架和没脚手架的差距

| 场景 | 没脚手架 | 有脚手架 |
|------|---------|---------|
| 新人启动 | 找文档、猜命令、踩坑，40 分钟 | `npm install && npm run dev`，5 分钟 |
| 配置密钥 | 改 config.js，提心吊胆 | 复制 .env.example，填自己的值 |
| 提交代码 | 不小心就提交了 .env | .gitignore 挡死了 |

## 六、进入 Iter 1

工程基础搭好了，接下来进入第一个开发迭代——**Iter 1：工具函数层。**

---

*下一篇：05-Iter 1——工具函数层（errors + password + jwt）。*