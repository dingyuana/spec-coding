# 成果 06 — TDD 测试：先写 25 条断言

> 对应教程：`tutorials/06-tdd-red-tutorial.md`  
> 实际文件：`tests/unit/*.test.js` + `tests/integration/auth.test.js`

---

## 📄 我们写出来的 5 个测试文件

所有测试加起来 **25 条断言**，覆盖了 SPEC 里定义的 4 个 Scenario。

### 测试 1：密码工具（5 条）

```javascript
// tests/unit/password.test.js
it('密码少于 6 位时应抛出错误')       // 测试边界
it('空密码时应抛出错误')                // 测试边界
it('应返回哈希后的密码')               // 测试正常路径
it('密码匹配时应返回 true')            // 测试验证
it('密码不匹配时应返回 false')         // 测试失败路径
```

### 测试 2：JWT 工具（3 条）

```javascript
// tests/unit/jwt.test.js
it('签发 token 应使用 user_id')        // payload 格式
it('有效 token 应返回 decoded payload') // 解码
it('无效 token 应抛出异常')             // 异常处理
```

### 测试 3：错误类（6 条）

```javascript
// tests/unit/errors.test.js
it('应携带 message 和 statusCode')     // 错误构造
it('默认 statusCode 应为 500')          // 默认值
it('INVALID_CREDENTIALS: 401')          // 预定义错误码
it('MISSING_PARAMS: 工厂函数')          // 动态错误
it('INTERNAL: 500')                     // 内部错误
it('应正确捕获堆栈')                    // 调试信息
```

### 测试 4：认证服务（3 条）

```javascript
// tests/unit/authService.test.js
it('用户名密码正确应返回 token')        // ✅ 正常登录
it('密码错误应抛出 INVALID_CREDENTIALS') // ❌ 密码错误
it('用户不存在应抛出 INVALID_CREDENTIALS') // ❌ 用户不存在
```

### 测试 5：集成测试（8 条）

```javascript
// tests/integration/auth.test.js
it('admin 正确密码应返回 200 + token')  // Scenario 1
it('JWT payload 应包含 user_id')         // Scenario 1（验证 token 内容）
it('正确用户名 + 错误密码应返回 401')    // Scenario 2
it('不存在的用户名应返回 401')           // Scenario 3
it('错误消息与密码错误完全一致')         // 防枚举攻击
it('缺少 username 应返回 400')           // Scenario 4
it('缺少 password 应返回 400')           // Scenario 4
it('两个字段都缺失应返回 400')           // Scenario 4
```

## 🎯 验证：跑测试会怎样？

```bash
$ npm test
Test Suites: 5 passed, 5 total
Tests:       25 passed, 25 total
```

> **全部绿色。** 这就是 TDD 的威力：先写测试 == 先定义"什么叫正确"，然后写代码让它正确。

---

下一步 → [成果 07：源码实现 — 从 RED 到 GREEN](results/07-green-result.md)