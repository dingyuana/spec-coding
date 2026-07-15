# 成果 04 — 脚手架：让代码跑起来

> 对应教程：`tutorials/04-scaffold-tutorial.md`  
> 实际文件：`package.json` + `.env` + `.gitignore`

---

## 📄 我们写出来的三个文件

### 1. package.json（项目身份证）

```json
{
  "scripts": {
    "start": "node src/index.js",      // 启动
    "dev": "node --watch src/index.js", // 开发（自动重启）
    "test": "jest --verbose"            // 跑测试
  },
  "dependencies": {
    "koa": "^2.15.3",           // Web 框架
    "bcryptjs": "^2.4.3",       // 密码加密
    "jsonwebtoken": "^9.0.2"   // JWT 令牌
  }
}
```

> `npm run dev` 一键启动，`npm test` 一键测试——新人不需要猜启动命令。

### 2. .env（密钥放这里，不提交 Git）

```ini
JWT_SECRET=dev-secret-key-change-in-production
JWT_EXPIRES_IN=86400    # 24 小时（单位：秒）
BCRYPT_ROUNDS=10        # 加密强度
```

> 还有一份 `.env.example` 作为模板。新人复制它就能用，不怕漏配置。

### 3. .gitignore（防手滑）

```
node_modules/    # 依赖包不提交
.env             # 密钥不提交
```

> 这两行堵住了最常见的两个安全事故。很多新手第一次提交就把 `.env` 带上去了——**`.gitignore` 是第一道安全防线。**

## 🎯 验证：能跑了吗？

```bash
cd user-login
npm install       # 装依赖（5 秒）
cp .env.example .env  # 配环境（2 秒）
npm run dev       # 启动！（1 秒）
```

从 clone 到跑起来，**5 分钟**。

> 没有脚手架的项目：新人花 40 分钟找怎么启动。  
> 有脚手架的项目：新人花 5 分钟 npm install。

---

下一步 → [成果 05：种子数据 — 预置用户](results/05-seed-result.md)