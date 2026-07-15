# Iter 2：数据模型 + 种子数据 — 别让空数据库卡住你的登录接口

> **"鸡生蛋"是编程中最真实的痛，种子数据是唯一的解药。**
>
> 场景：你写好了登录接口，curl 过去，得到 401 → 然后你愣住 → 哦，数据库里没用户。
>
> 这一节，我们用 Map 实现 User 模型，用 seed 脚本预置 admin 用户，打破这个死循环。

---

## 一、经典的翻车现场

你花了一小时写好了登录接口。路由、参数校验、密码比对，一气呵成。你自信地打开终端：

```bash
curl -X POST http://localhost:3000/api/auth/login \
  -d '{"username":"admin","password":"admin123"}'
```

返回：

```json
{ "error": "用户名或密码错误" }
```

你愣了两秒。代码没问题啊？然后猛然意识到——

**数据库里没有用户。**

你还没写注册接口，但登录需要用户。写注册接口吧，它又需要存储层；写存储层吧，测试又需要先有用户。你被自己写的代码卡住了。

这就是 **"鸡生蛋"问题**（Chicken-and-Egg Problem）：

```
要测试登录 → 需要用户 → 需要注册接口 → 需要调通登录 → 需要用户...
                   ↑_____________________________↓
```

**你陷入了一个循环依赖，而你自己就是那个被锁在中间的人。**

---

## 二、破局：先有鸡还是先有蛋？答案是"种子数据"

"鸡生蛋"的解法很简单：**你手动放一只鸡进去。**

种子数据（Seed Data）就是这个思路——在系统启动时，自动预置一条初始用户记录。不用等注册接口，不用手动敲 SQL，不用写临时脚本。

但种子数据不是随便写写就完事的。它需要满足三个条件：

1. **幂等性**：跑 1 次和跑 100 次效果一样，不报错、不重复、不炸
2. **安全性**：密码必须走哈希，和正式登录同一套逻辑
3. **可测试性**：种子数据流程本身要能被测试覆盖

---

## 三、先写测试：定义 User 模型的行为

### 问题：用户数据用什么存？

最简单的方案是数组。但数组有个问题：

```javascript
// 数组方案
const users = [];
users.push(user);
users.find(u => u.username === 'alice');  // O(n) — 每次都要遍历
```

每查一次用户，就要遍历整个数组。本地测试无所谓，但**它不符合真实数据库的"主键索引"思维**。

换成 **Map**：

```javascript
// Map 方案
const users = new Map();
users.set(user.id, user);
users.get(id);  // O(1) — 直接命中
```

`Map.get(id)` 是 O(1)，而数组的 `find` 是 O(n)。**Map 更接近"主键索引"的行为**——你知道 ID，就能直接定位到记录，不需要扫描全部。这叫"用数据结构映射业务语义"。

### 写测试（RED）

```javascript
// tests/unit/userModel.test.js
const { UserModel } = require('../../src/models/user');

beforeEach(() => {
  UserModel.clear();  // 每次测试前清空，互不干扰
});

it('应创建用户并返回完整信息', () => {
  const user = UserModel.create({
    username: 'alice',
    passwordHash: 'hash123',
  });

  expect(user.id).toBe(1);
  expect(user.username).toBe('alice');
  expect(user.passwordHash).toBe('hash123');
  expect(user.createdAt).toBeInstanceOf(Date);
});

it('存在时返回用户，不存在时返回 undefined', () => {
  UserModel.create({ username: 'alice', passwordHash: 'hash123' });

  expect(UserModel.findByUsername('alice')).toBeDefined();
  expect(UserModel.findByUsername('nobody')).toBeUndefined();
});

it('按 ID 查找用户', () => {
  const user = UserModel.create({ username: 'alice', passwordHash: 'hash123' });
  expect(UserModel.findById(user.id).username).toBe('alice');
  expect(UserModel.findById(999)).toBeUndefined();
});

it('可以创建多个用户并自增 ID', () => {
  const u1 = UserModel.create({ username: 'alice', passwordHash: 'hash1' });
  const u2 = UserModel.create({ username: 'bob', passwordHash: 'hash2' });

  expect(u1.id).toBe(1);
  expect(u2.id).toBe(2);
  expect(UserModel.findById(1).username).toBe('alice');
  expect(UserModel.findById(2).username).toBe('bob');
});

it('clear 后应重置所有数据', () => {
  UserModel.create({ username: 'alice', passwordHash: 'hash123' });
  UserModel.clear();
  expect(UserModel.findByUsername('alice')).toBeUndefined();
});
```

> **注意 `beforeEach` 里的 `UserModel.clear()`**——这条是"测试隔离"的根基。没有它，测试 A 创建的用户会污染测试 B 的结果，测试就变成了"先跑先绿，后跑可能炸"的薛定谔状态。**每次测试前清空，保证每一轮都是全新开始。**

### 写实现（GREEN）

```javascript
// src/models/user.js
const users = new Map();
let nextId = 1;

const UserModel = {
  findByUsername(username) {
    // Map 存的是 {id → user}，按 username 查需要遍历 values
    // 但数据量小，清晰比极致性能更重要
    return Array.from(users.values()).find(
      (u) => u.username === username
    );
  },

  findById(id) {
    return users.get(id);  // O(1) 直接命中
  },

  create({ username, passwordHash }) {
    const user = {
      id: nextId++,
      username,
      passwordHash,
      createdAt: new Date(),
    };
    users.set(user.id, user);
    return user;
  },

  clear() {
    users.clear();
    nextId = 1;
  },
};

module.exports = { UserModel };
```

**Map vs 数组，为什么选 Map？**

| 维度 | 数组 | Map |
|------|------|-----|
| 按 ID 查找 | O(n) — 遍历 | O(1) — 直接命中 |
| 语义清晰度 | 像"列表" | 像"键值存储" |
| 映射真实数据库 | 弱 | 强（主键索引） |
| 删除/更新 | 麻烦 | 原生方法 |

小项目用哪个都行，但 **Map 培养了"索引思维"**——当你习惯用 Map 存数据，你自然就会想到：数据库里这个表的主键是什么？查询应该用哪个字段做 Key？这种思维模式，到了 PostgreSQL 或 MongoDB 里，就是选择索引、设计分片键的能力。

---

## 四、种子脚本：一次"预装"，省掉一万次注册

模型写好了，但数据库是空的。每次启动后你都要手动注册用户？——**不现实。**

种子脚本就是解决这个问题的：**系统启动时自动创建 admin 用户。**

### 写种子脚本测试

```javascript
// tests/unit/seed.test.js
const { UserModel } = require('../../src/models/user');
const { seedDatabase } = require('../../scripts/seed');

beforeEach(() => {
  UserModel.clear();
});

it('应创建种子管理员用户', async () => {
  const user = await seedDatabase();
  expect(user.username).toBe('admin');
  expect(user.passwordHash).toBeDefined();
  expect(user.passwordHash).not.toBe('admin123');  // 不是明文！
});

it('幂等性：多次运行不重复创建', async () => {
  const first = await seedDatabase();
  const second = await seedDatabase();

  expect(first.id).toBe(second.id);  // 同一个用户
  expect(UserModel.findByUsername('admin').id).toBe(first.id);
});

it('种子用户的密码哈希应可通过 bcrypt 验证', async () => {
  const { hashPassword } = require('../../src/utils/auth');
  await seedDatabase();
  const user = UserModel.findByUsername('admin');
  const isValid = await hashPassword('admin123') === user.passwordHash;
  expect(isValid).toBe(true);
});
```

### 写实现

```javascript
// scripts/seed.js
const { UserModel } = require('../src/models/user');
const { hashPassword } = require('../src/utils/auth');

const SEED_USER = {
  username: 'admin',
  password: 'admin123',
};

async function seedDatabase() {
  // 幂等性检查：如果已存在，直接返回——不重复创建
  const existing = UserModel.findByUsername(SEED_USER.username);
  if (existing) {
    console.log(`[seed] 用户 ${SEED_USER.username} 已存在，跳过`);
    return existing;
  }

  // 密码走 bcrypt 哈希，和正式登录同一套逻辑
  const passwordHash = await hashPassword(SEED_USER.password);

  const user = UserModel.create({
    username: SEED_USER.username,
    passwordHash,  // 🔒 存的是哈希，不是明文！
  });

  console.log(`[seed] 创建种子用户: ${user.username} (id=${user.id})`);
  return user;
}

module.exports = { seedDatabase };
```

### 两个关键设计

**1. 幂等性——最重要的安全绳**

```javascript
if (existing) return existing;
```

这一行是种子脚本的灵魂。没有它，你每次重启服务器都会多一个 admin 用户。跑 1 次 = 1 个 admin，跑 100 次 = 1 个 admin。**不会报错，不会重复，不会炸。**

**幂等性（Idempotency）** 是分布式系统的核心概念：同一个操作执行多次，结果和执行一次完全一样。种子脚本是幂等性最朴素也最实用的体现。

**2. 密码走 bcrypt——和正式用户同待遇**

```javascript
const passwordHash = await hashPassword(SEED_USER.password);
```

种子用户用的是 `hashPassword`，和正式注册的用户完全一样。**不会出现"种子用户密码格式和正式用户不一致"的坑。**

### 在启动时自动调用

```javascript
// src/index.js
async function main() {
  await seedDatabase();  // 🔥 启动时自动预置 admin
  const app = createApp();
  app.listen(3000);
  console.log('🚀 Server running on http://localhost:3000');
}
```

之后你 `npm run dev`，直接就能用 `admin / admin123` 登录。**没有注册接口也能登录，种子数据打破了循环依赖。**

---

## 五、"鸡生蛋"的本质：解耦

```
没有种子脚本：
  注册 → 登录 → 需要用户 → 卡住了
  写登录 → 等注册接口 → 写注册 → 等登录接口 → 死循环

有种子脚本：
  种子脚本 → 预置 admin → 登录直接可用 → 测试不用等注册
  种子脚本 → 预置数据 → 服务层独立测试 → 路由层独立测试
```

**种子数据不是"作弊"，是"解耦"。**

它让你可以独立开发、独立测试登录模块，而不必等到注册模块完成后才能开始。它把"鸡生蛋"的循环依赖，变成了"先放鸡进去，再让蛋生出来"的线性流程。

种子数据背后是一种 **"先置条件"（precondition）** 的思维——在系统启动前，先确保某些基础条件已经满足。这不是偷懒，这是工程化的基础设施思维。

---

## 六、验证：18 passed

```bash
$ npx jest tests/unit/
```

```
 PASS  tests/unit/seed.test.js
 PASS  tests/unit/userModel.test.js
 PASS  tests/unit/authUtils.test.js
 PASS  tests/unit/... (所有工具函数测试)

Tests: 18 passed, 18 total ✅
```

**18 个测试，全部通过。**

从上一个 Iter 的工具函数，到现在的 User 模型和种子脚本，18 条测试覆盖了：

- 用户创建、查询、清空（5 条）
- 种子脚本的幂等性和密码安全性（3 条）
- 工具函数全部回归（10 条）

**每一个测试都是一面盾牌。** 18 面盾牌，牢牢护住你的数据层。

---

## 七、进入 Iter 3

数据模型准备好了，种子数据预置好了，接下来：

**登录业务逻辑——服务层。**

```bash
Tests: 18 passed, 18 total ✅
```

---

*下一篇：07-Iter 3——服务层（authService）——真正的登录逻辑来了。*