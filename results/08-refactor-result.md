# 成果 08 — REFACTOR：完整项目回顾

> 对应教程：`tutorials/08-refactor-tutorial.md`  
> 最终成果：全部通过 ✅

---

## 📦 项目完整目录

```
user-login/
├── SPEC.md              # 业务契约
├── PLAN.md              # 任务看板
├── AGENT.md             # 编码规范
├── package.json         # 依赖与脚本
├── .env / .env.example  # 环境配置
├── .gitignore           # 忽略规则
├── scripts/
│   └── seed.js          # 种子数据
├── src/
│   ├── index.js         # 入口
│   ├── app.js           # 应用工厂
│   ├── config/index.js  # 配置
│   ├── routes/auth.js   # 路由
│   ├── controllers/authController.js
│   ├── services/authService.js  # 业务逻辑
│   ├── models/user.js   # 数据模型
│   ├── middleware/
│   │   ├── errorHandler.js  # 异常处理
│   │   └── auth.js          # 鉴权
│   └── utils/
│       ├── errors.js    # 错误类
│       ├── jwt.js       # JWT 工具
│       └── password.js  # 加密工具
├── tests/
│   ├── unit/
│   │   ├── password.test.js   # 5 条
│   │   ├── jwt.test.js        # 3 条
│   │   ├── errors.test.js     # 6 条
│   │   └── authService.test.js # 3 条
│   └── integration/
│       └── auth.test.js       # 8 条
├── tutorials/           # 8 篇教程
└── results/             # 8 篇成果展示（本文所在目录）
```

## 🧪 最终验证

```bash
$ npm test
Test Suites: 5 passed, 5 total
Tests:       25 passed, 25 total
```

## 🔗 回顾：从零到一的全过程

```
第 1 步：写 SPEC → 确定"做什么"（4 个 Scenario）
第 2 步：写 PLAN → 确定"先做什么"（P0-P4）
第 3 步：写 AGENT → 确定"做到什么标准"（4 条禁止令）
第 4 步：搭脚手架 → 让项目能跑（package.json / .env / .gitignore）
第 5 步：写种子 → 预置 admin 用户（scripts/seed.js）
第 6 步：写测试 → 把验收变成断言（25 条测试，全部 RED）
第 7 步：写代码 → 让测试变绿（12 个源码文件）
第 8 步：验证回顾 → 全部通过 ✅
```

## 💡 一句话总结

```
SDD（先想清楚）→ TDD（先写测试）→ 实现（让测试通过）→ 验证（全部绿色）
```

这个流程适用于**任何项目**，不只是一个登录模块。

---

⭐ **全部完成。** 现在你可以用 `curl` 测试实际效果：

```bash
# 正常登录
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
# → {"token":"eyJ..."}

# 密码错误
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrong"}'
# → {"error":"用户名或密码错误"}
```