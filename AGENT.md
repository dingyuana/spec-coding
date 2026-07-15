# 用户登录模块 — AGENT

## 命名规范
| 类型 | 风格 | 示例 |
|------|------|------|
| 变量/函数 | camelCase | findByUsername |
| 类 | PascalCase | AppError |
| 文件目录 | kebab-case | authService.js |

## 分层规范（单向依赖）
```
config/ → 纯配置
utils/  → 纯工具函数，不依赖项目内其他模块
models/ → 数据存取，依赖 utils
services/ → 业务逻辑，依赖 models + utils
controllers/ → 参数校验 + 调用 service
routes/ → 路由映射
middleware/ → 跨切面逻辑
app.js + index.js → 组装
```

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