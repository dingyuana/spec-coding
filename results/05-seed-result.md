# 成果 05 — 种子数据：预置 admin 用户

> 对应教程：`tutorials/05-seed-tutorial.md`  
> 实际文件：`scripts/seed.js`

---

## 📄 我们写出来的文件

打开 `scripts/seed.js`，它只做一件事：**确保 admin 用户存在。**

### 完整代码（只有 20 行）

```javascript
const SEED_USER = {
  username: 'admin',
  password: 'admin123',
  role: 'admin',
};

async function seedDatabase() {
  // 检查是否已存在（幂等性）
  const existing = UserModel.findByUsername(SEED_USER.username);
  if (existing) {
    console.log(`[seed] 用户 ${SEED_USER.username} 已存在，跳过`);
    return existing;  // 跑第二次不重复创建
  }

  // 密码走 bcrypt 加密
  const passwordHash = await hashPassword(SEED_USER.password);
  const user = UserModel.create({
    username: SEED_USER.username,
    passwordHash,  // 🔒 存入的是哈希，不是明文
    role: SEED_USER.role,
  });
  return user;
}
```

### 两个关键设计

**1. 幂等性（跑多少次都一样）**

```
第一次运行：admin 不存在 → 创建 → 成功 ✅
第二次运行：admin 已存在 → 跳过 → 成功 ✅
第 N 次运行：admin 已存在 → 跳过 → 成功 ✅
```

不会报错，不会重复，不会炸。

**2. 密码走 bcrypt**

```javascript
const passwordHash = await hashPassword('admin123');
// 存入的是：$2a$10$...（bcrypt 哈希，不可逆）
// 不是：admin123（明文，危险！）
```

### 种子脚本什么时候跑？

```javascript
// src/index.js
async function main() {
  await seedDatabase();          // 启动时自动预置 admin
  const app = createApp();
  app.listen(3000);
}
```

所以你 `npm run dev` 后，直接就能用 `admin / admin123` 登录。

> **没有种子脚本：** 你要先写注册接口才能注册用户，再拿注册的用户测登录。  
> **有种子脚本：** 启动即用，不需要等注册接口。

---

下一步 → [成果 06：TDD 测试 — 25 条断言](results/06-tdd-result.md)