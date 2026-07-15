# 成果 07 — 源码实现：从 RED 到 GREEN

> 对应教程：`tutorials/07-green-tutorial.md`  
> 实际文件：`src/` 下的 12 个文件

---

## 📄 我们写出来的源码

### 入口：src/index.js

```javascript
async function main() {
  await seedDatabase();          // 启动时预置 admin 用户
  const app = createApp();
  app.listen(3000);
}
```

### 路由：src/routes/auth.js

```javascript
const router = new Router({ prefix: '/api/auth' });
router.post('/login', AuthController.login);  // 唯一接口
```

### 控制器：src/controllers/authController.js

```javascript
async login(ctx) {
  const { username, password } = ctx.request.body;
  if (!username || !password) {
    throw Errors.MISSING_PARAMS('用户名和密码不能为空');  // 参数校验
  }
  const { token } = await AuthService.login({ username, password });
  ctx.status = 200;
  ctx.body = { token };  // 匹配 SPEC 的响应格式
}
```

### 服务层：src/services/authService.js

```javascript
async login({ username, password }) {
  const user = UserModel.findByUsername(username);
  if (!user) throw Errors.INVALID_CREDENTIALS;        // 用户不存在
  const isValid = await verifyPassword(password, user.passwordHash);
  if (!isValid) throw Errors.INVALID_CREDENTIALS;      // 密码错误
  const token = signToken(user.id);
  return { token };
}
```

### 工具函数：src/utils/jwt.js

```javascript
function signToken(userId) {
  return jwt.sign({ user_id: userId }, config.jwt.secret, { expiresIn: 86400 });
}
function verifyToken(token) {
  return jwt.verify(token, config.jwt.secret);
}
```

### 全局异常处理：src/middleware/errorHandler.js

```javascript
function errorHandler(err, ctx) {
  if (err instanceof AppError) {
    ctx.status = err.statusCode;
    ctx.body = { error: err.message };  // 统一格式
    return;
  }
  ctx.status = 500;
  ctx.body = { error: '服务器内部错误' };
}
```

## 🎯 验证：从 RED 到 GREEN

```
RED 阶段：写了 25 条测试，全部失败（红色）
    ↓  写了 12 个源码文件
GREEN 阶段：25 条测试全部通过（绿色）
```

```bash
$ npm test
Test Suites: 5 passed, 5 total
Tests:       25 passed, 25 total
```

> **RED → GREEN 的核心：不是一口气写完所有代码，而是每次改一个文件、跑一次测试、红变绿一个。**

---

下一步 → [成果 08：REFACTOR — 完整回顾](results/08-refactor-result.md)