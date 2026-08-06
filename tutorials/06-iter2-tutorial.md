# Iter 2：数据模型 + 种子数据——别让空数据库卡住你的登录接口

> **"鸡生蛋"是编程中最真实的痛，种子数据是唯一的解药。**
>
> 场景：你写好了登录接口，curl 过去，得到 401 → 然后你愣住 → 哦，数据库里没用户。
>
> 这一节，我们用 Map 实现 User 模型，用 seed 脚本预置 admin 用户，打破这个死循环。

---

## 一、理论：数据模型设计、种子数据与幂等性

### 1.1 经典的"鸡生蛋"问题

登录接口需要用户才能测试，但注册接口需要登录才能调通。你被自己写的代码卡住了：

```
要测试登录 → 需要用户 → 需要注册接口 → 需要调通登录 → 需要用户...
                 ↑_____________________________↓
```

![](imgs/06/01-break-circular-dependency.svg)

**种子数据（Seed Data）** 就是解法——在系统启动时，自动预置一条初始用户记录。不用等注册接口，不用手动敲 SQL，不用写临时脚本。

### 1.2 数据模型设计的三个原则

对于一个内存数据模型（本项目暂未引入数据库），设计时要考虑：

1. **查询效率**：按 ID 查找应该是 O(1)，而不是 O(n)
2. **测试隔离**：必须能快速清空数据，保证测试之间互不干扰
3. **行为清晰**：API 命名直观，语义明确

### 1.3 幂等性（Idempotency）

种子脚本必须满足**幂等性**——同一个操作执行多次，结果和执行一次完全一样。

```
第 1 次运行：创建 admin 用户
第 2 次运行：检测到 admin 已存在，跳过
第 100 次运行：检测到 admin 已存在，跳过
```

**不会报错、不会重复创建、不会炸。**

---

## 二、本项目实际代码

### 2.1 `src/config/index.js` — 配置集中管理

```javascript
// src/config/index.js
/**
 * 配置
 * Iter 2: 数据模型
 */
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(__dirname, '../../.env') });

const config = {
  port: parseInt(process.env.PORT, 10) || 3000,
  jwt: {
    secret: process.env.JWT_SECRET,
    expiresIn: parseInt(process.env.JWT_EXPIRES_IN, 10) || 86400,
  },
  bcrypt: {
    rounds: parseInt(process.env.BCRYPT_ROUNDS, 10) || 10,
  },
};

if (!config.jwt.secret) {
  console.error('[FATAL] JWT_SECRET 未设置');
  process.exit(1);
}

module.exports = config;
```

**设计要点：**
- 从 `.env` 加载配置，不用硬编码
- `parseInt` + `||` 默认值——环境变量缺失时不会崩
- **启动时校验**：如果 `JWT_SECRET` 没设置，直接 `process.exit(1)`——**fail fast**，不让系统带着安全隐患运行
- 集中管理——`jwt.js`、`seed.js` 都引用同一个 config 对象

---

### 2.2 `src/models/user.js` — 内存 User 模型

```javascript
// src/models/user.js
/**
 * User 模型
 * Iter 2: 数据模型层 — 内存 Map 存储
 */
const users = new Map();
let nextId = 1;

const UserModel = {
  findByUsername(username) {
    return Array.from(users.values()).find((u) => u.username === username);
  },

  findById(id) {
    return users.get(id);
  },

  create({ username, passwordHash }) {
    const now = new Date();
    const user = { id: nextId++, username, passwordHash, createdAt: now };
    users.set(user.id, user);
    return user;
  },

  clear() {
    users.clear();
    nextId = 1;
  },
};

module.exports = UserModel;
```

**为什么用 Map 不用数组？**

| 维度 | 数组 | Map |
|------|------|-----|
| 按 ID 查找 | O(n) — 遍历 | O(1) — 直接命中 |
| 语义清晰度 | 像"列表" | 像"键值存储" |
| 映射真实数据库 | 弱 | 强（主键索引） |
| 删除/更新 | 麻烦 | 原生方法 |

`Map.get(id)` 是 O(1)，而数组的 `find` 是 O(n)。**Map 更接近"主键索引"的行为**——你知道 ID 就能直接定位到记录，不需要扫描全部。

**`clear()` 方法为什么重要？** 它是测试隔离的根基。每次测试前调用 `clear()`，保证所有测试从同一个干净状态开始，互不干扰。

#### 测试：`tests/unit/userModel.test.js`（8 条测试）

```javascript
// tests/unit/userModel.test.js
/**
 * User 模型 — TDD 测试
 * Iter 2: 数据模型层
 */

const UserModel = require('../../src/models/user');

describe('UserModel', () => {
  beforeEach(() => {
    UserModel.clear();
  });

  describe('create', () => {
    it('应创建用户并返回完整信息', () => {
      const user = UserModel.create({ username: 'alice', passwordHash: 'hash123' });
      expect(user.id).toBe(1);
      expect(user.username).toBe('alice');
      expect(user.passwordHash).toBe('hash123');
      expect(user.createdAt).toBeInstanceOf(Date);
    });
  });

  describe('findByUsername', () => {
    it('存在时返回用户', () => {
      UserModel.create({ username: 'alice', passwordHash: 'hash123' });
      const user = UserModel.findByUsername('alice');
      expect(user).toBeDefined();
      expect(user.username).toBe('alice');
    });

    it('不存在时返回 undefined', () => {
      const user = UserModel.findByUsername('nobody');
      expect(user).toBeUndefined();
    });
  });

  describe('findById', () => {
    it('存在时返回用户', () => {
      const created = UserModel.create({ username: 'alice', passwordHash: 'hash123' });
      const user = UserModel.findById(created.id);
      expect(user).toBeDefined();
      expect(user.id).toBe(created.id);
    });

    it('不存在时返回 undefined', () => {
      expect(UserModel.findById(999)).toBeUndefined();
    });
  });

  describe('clear', () => {
    it('应清空所有用户', () => {
      UserModel.create({ username: 'alice', passwordHash: 'hash123' });
      UserModel.clear();
      expect(UserModel.findByUsername('alice')).toBeUndefined();
    });
  });
});
```

**8 条测试覆盖了什么：**

| 分组 | 测试 | 断言 |
|------|------|------|
| create | 创建用户返回完整信息 | id + username + passwordHash + createdAt |
| findByUsername | 存在时返回用户 | 返回正确的用户对象 |
| findByUsername | 不存在时返回 undefined | 返回 undefined |
| findById | 存在时返回用户 | 通过 ID 找到用户 |
| findById | 不存在时返回 undefined | 返回 undefined |
| clear | 清空所有用户 | 创建后清空，查不到 |

> **注意 `beforeEach` 里的 `UserModel.clear()`**——这是"测试隔离"的根基。没有它，测试 A 创建的用户会污染测试 B 的结果。**每次测试前清空，保证每一轮都是全新开始。**

---

### 2.3 `scripts/seed.js` — 种子数据脚本

```javascript
// scripts/seed.js
/**
 * 种子数据脚本
 * Iter 2: 数据模型层
 * 预置 admin 用户，支持幂等性
 */
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

const UserModel = require('../src/models/user');
const { hashPassword } = require('../src/utils/password');

const SEED_USER = { username: 'admin', password: 'admin123' };

async function seedDatabase() {
  const existing = UserModel.findByUsername(SEED_USER.username);
  if (existing) {
    console.log(`[seed] ${SEED_USER.username} 已存在，跳过`);
    return existing;
  }
  const passwordHash = await hashPassword(SEED_USER.password);
  const user = UserModel.create({ username: SEED_USER.username, passwordHash });
  console.log(`[seed] ${user.username} 创建成功 (id=${user.id})`);
  return user;
}

if (require.main === module) {
  seedDatabase().then(() => process.exit(0)).catch((err) => { console.error(err.message); process.exit(1); });
}

module.exports = { seedDatabase, SEED_USER };
```

**两个关键设计：**

**1. 幂等性——最重要的安全绳**

```javascript
const existing = UserModel.findByUsername(SEED_USER.username);
if (existing) {
  console.log(`[seed] ${SEED_USER.username} 已存在，跳过`);
  return existing;
}
```

这一行是种子脚本的灵魂。没有它，你每次重启服务器都会多一个 admin 用户。幂等性保证：跑 1 次 = 1 个 admin，跑 100 次 = 1 个 admin。**不会报错，不会重复，不会炸。**

**2. 密码走 bcrypt——和正式用户同待遇**

```javascript
const passwordHash = await hashPassword(SEED_USER.password);
```

种子用户用的是 `hashPassword`，和正式注册的用户完全一样。**不会出现"种子用户密码格式和正式用户不一致"的坑。**

**3. 支持命令行直接运行**

```javascript
if (require.main === module) {
  seedDatabase()...
}
```

这段代码让 `scripts/seed.js` 既可以作为模块被主程序 `require`，也可以直接 `node scripts/seed.js` 独立运行。

---

### 2.4 在启动时自动调用种子脚本

```javascript
// src/index.js
async function main() {
  await seedDatabase();  // 🔥 启动时自动预置 admin
  const app = createApp();
  app.listen(config.port);
  console.log(`🚀 Server running on http://localhost:${config.port}`);
}
```

之后你 `npm run dev`，直接就能用 `admin / admin123` 登录。**没有注册接口也能登录，种子数据打破了循环依赖。**

---

## 三、"鸡生蛋"的本质：解耦

```
没有种子脚本：
  注册 → 登录 → 需要用户 → 卡住了
  写登录 → 等注册接口 → 写注册 → 等登录接口 → 死循环

有种子脚本：
  种子脚本 → 预置 admin → 登录直接可用 → 测试不用等注册
  种子脚本 → 预置数据 → 服务层独立测试 → 路由层独立测试
```

**种子数据不是"作弊"，是"解耦"。**

![](imgs/06/02-idempotent.svg)

它让你可以独立开发、独立测试登录模块，而不必等到注册模块完成后才能开始。它把"鸡生蛋"的循环依赖，变成了"先放鸡进去，再让蛋生出来"的线性流程。

种子数据背后是一种 **"先置条件"（precondition）** 的思维——在系统启动前，先确保某些基础条件已经满足。这不是偷懒，这是工程化的基础设施思维。

---

## 四、验证：Iter 1 + Iter 2 全部通过

```bash
$ npx jest tests/unit/

Test Suites: 4 passed, 4 total
Tests:       21 passed, 21 total ✅
```

从上一个 Iter 的工具函数，到现在的 User 模型和种子脚本，21 条测试覆盖了：

- 工具函数全部回归（13 条）
- 用户创建、查询、清空（8 条）

**每一个测试都是一面盾牌。** 21 面盾牌，牢牢护住你的数据层。

---

## 五、进入 Iter 3

数据模型准备好了，种子数据预置好了，接下来：

**登录业务逻辑——服务层。**

```
Tests: 21 passed, 21 total ✅
```

---

*下一篇：07-Iter 3——服务层（authService）——真正的登录逻辑来了。*