# 成果 00 — SDD+TDD 框架总览

> 本文是理论结合实战的成果展示。  
> 对应教程：`tutorials/00-sdd-tdd-intro.md`

---

## 📁 项目结构（这是我们最终要实现的）

```
user-login/
├── SPEC.md              # 业务契约
├── PLAN.md              # 任务看板
├── AGENT.md             # 编码规范
├── .env                 # 环境配置
├── .gitignore           # 忽略规则
├── package.json         # 依赖与脚本
├── scripts/
│   └── seed.js          # 种子数据
├── src/                 # 源码（12个文件）
├── tests/               # 测试（25条）
└── tutorials/           # 教程（8篇）
```

## 🧱 项目技术栈

```
语言：      Node.js 18+
框架：      Koa 2
密码：      bcryptjs（≈10 rounds）
令牌：      jsonwebtoken（24h 过期）
测试：      Jest + Supertest
```

## 🎯 我们要实现的功能

只有一个接口，但覆盖了 4 个完整场景：

| 场景 | 你输入 | 你得到 |
|------|--------|--------|
| ✅ 正常登录 | `{ "username":"admin", "password":"admin123" }` | `200` + JWT Token |
| ❌ 密码错误 | `{ "username":"admin", "password":"wrong" }` | `401` + `"用户名或密码错误"` |
| ❌ 用户不存在 | `{ "username":"hacker", "password":"x" }` | `401` + `"用户名或密码错误"`（一样！） |
| ❌ 参数缺失 | `{ "username":"admin" }` | `400` + `"用户名和密码不能为空"` |

> **为什么用户不存在和密码错误返回一样的消息？**  
> 防止攻击者通过错误消息猜出哪些用户存在。这是安全设计，不是 bug。

## ✅ 质量标准

这个项目完成时，我们会通过：

```
Test Suites: 5 passed, 5 total
Tests:       25 passed, 25 total
```

---

下一步 → [成果 01：SPEC.md — 把需求写成契约](results/01-spec-result.md)