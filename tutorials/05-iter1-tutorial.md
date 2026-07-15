# Iter 1：工具函数层——先写测试，再写代码

> **场景带入 → 发现问题 → 方案迭代 → 原理拆解 → 效果对比 → 情绪升华**

---

> 这是**第一个真正的开发迭代**。前 4 篇文章我们在"搭框架"，现在开始写代码。
> 
> 按照 PLAN，Iter 1 只做 3 个文件，每个文件先写测试，再写实现。**一次只做一件事，做完再测，测完再做下一件。**

---

## 一、"工具函数不用测了吧"——这句 Flag 你立过吗？

来，对号入座。

你写了一个工具函数，就十几行。你看着它，心想：**"这么简单，不用测了吧，脑跑一遍就知道没问题。"**

然后你上线了。

然后线上炸了。

来看看真实世界里，那些"不用测"的工具函数是怎么翻车的——

**翻车案例 #1：密码哈希慢如牛**
```javascript
// 猜猜哪里有问题？
const salt = await bcrypt.genSalt();  // 没传 rounds！
```
`bcrypt.genSalt()` 的默认 rounds 是 **10**……吗？不，某些旧版本默认是 **6**？某些环境是 **8**？你到底得到的是什么？你根本不知道。不写测试，这个参数永远不会被审视。结果就是你的登录接口慢到用户以为网站挂了。

**翻车案例 #2：Token 永不过期**
```javascript
jwt.sign({ user_id: 1 }, secret);  // expiresIn 呢？忘了吧
```
没有 `expiresIn`，这个 token **永远不会过期**。攻击者只要拿到一个 token，就可以永久登录你的系统。这不是 Bug，这是**安全漏洞**。

**翻车案例 #3：错误码的"薛定谔"状态**
```javascript
throw new Error('wrong');
throw new Error('WRONG');
throw new Error('密码错误');
```
前端说："啊？你到底抛什么？我怎么知道该 catch 哪个？"

---

**工具函数的问题，从来不是"能不能跑"，而是"边界条件对不对、参数传没传全、行为是不是可预测"。**

而这恰恰是肉眼 review 最容易漏掉的地方——你写的时候觉得"肯定没问题"，实际上每个参数、每个边界、每种输入都可能埋雷。

**怎么治？——先写测试，再写代码。让测试当你的第二个大脑。**

![](imgs/05/02-utils-independence.svg)

---

## 二、RED #1 → GREEN #1：errors——你的错误也需要"身份证"

三个工具函数 `errors`、`password`、`jwt` 没有依赖关系，先写谁都行。但我们从 `errors` 开始，因为它太基础了——`authService` 里到处都在 `throw Errors.INVALID_CREDENTIALS`。

**如果错误没有标准格式，你的整个应用的错误处理就是一团乱麻。**

### 🔴 RED：先让测试红起来

打开 `tests/unit/errors.test.js`，写下第一组测试：

```javascript
it('AppError 应携带 message 和 statusCode', () => {
  const err = new AppError('自定义错误', 400);
  expect(err.message).toBe('自定义错误');
  expect(err.statusCode).toBe(400);
});

it('INVALID_CREDENTIALS: 401 用户名或密码错误', () => {
  expect(Errors.INVALID_CREDENTIALS.statusCode).toBe(401);
  expect(Errors.INVALID_CREDENTIALS.message).toBe('用户名或密码错误');
});
```

好，跑一下——

```bash
$ npx jest tests/unit/errors.test.js
```

**💥 红色。报错，`Cannot find module`。**

对，`errors.js` 还不存在。测试理所当然地红了。

**但是，注意这个红色——它是有意义的红色。** 它精确告诉了你："你要写哪个文件，它需要导出什么。" 这就是 RED 的价值：不是失败，是**指引**。

### 🟢 GREEN：让红色变绿

```javascript
// src/utils/errors.js
class AppError extends Error {
  constructor(message, statusCode = 500) {
    super(message);
    this.name = 'AppError';
    this.statusCode = statusCode;
  }
}
const Errors = {
  INVALID_CREDENTIALS: new AppError('用户名或密码错误', 401),
  MISSING_PARAMS: (msg) => new AppError(msg, 400),
  INTERNAL: new AppError('服务器内部错误', 500),
};

module.exports = { AppError, Errors };
```

注意到 `statusCode = 500` 这个默认值了吗？**如果你忘了传状态码，它不会静默地变成 `undefined`，而是稳稳地落在 500。** 这就是防御性编程——在源头堵住不确定性。

再跑一次——

```bash
$ npx jest tests/unit/errors.test.js
```

**🟢 一片绿。6 条测试，全部通过。**

这个"从红到绿"的过程用了多久？大概 30 秒。但就是这 30 秒，你已经确定了：
- 所有错误都有统一的 `message` + `statusCode` 格式
- 所有预定义错误都不会因为拼写而出错
- 前端可以放心地根据 `statusCode` 做错误处理

**这就是第一个 RED→GREEN 循环。爽不爽？别急，更爽的在后面。**

---

## 三、RED #2 → GREEN #2：password——边界条件就是你的"安全防线"

密码工具是整个系统里**最不能出差错**的地方。

为什么？因为密码相关 Bug 的后果不是"功能不能用"，而是**安全漏洞**。

想象一下：如果 `hashPassword` 收到一个空字符串 `''`，它应该怎么做？是抛异常？还是默默地生成一个空密码的哈希？

如果你选择了后者——恭喜你，攻击者只要用空字符串就能登录任何账号。

### 🔴 RED：先写边界条件

```javascript
// tests/unit/password.test.js
it('密码少于 6 位时应抛出错误', async () => {
  await expect(hashPassword('12')).rejects.toThrow('密码长度不能少于 6 位');
});

it('密码为空时应抛出错误', async () => {
  await expect(hashPassword('')).rejects.toThrow('密码长度不能少于 6 位');
});

it('密码为 undefined 时应抛出错误', async () => {
  await expect(hashPassword(undefined)).rejects.toThrow('密码长度不能少于 6 位');
});

it('密码匹配时应返回 true', async () => {
  bcrypt.compare.mockResolvedValue(true);
  const result = await verifyPassword('mypassword', 'hashed-value');
  expect(result).toBe(true);
});
```

跑一下——

```bash
$ npx jest tests/unit/password.test.js
```

**💥 红色。Module not found。** 意料之中。

**但是仔细看看这段测试代码，它暴露了一个关键设计问题：密码验证的时候，我们 mock 了 bcrypt。**

为什么？因为真的 bcrypt 哈希一次要 **几十毫秒**，而 mock 版 **1 微秒**就返回了。你的测试不应该因为加密速度而变慢——测试跑得越快，你才越愿意跑它。

> **一条好测试的黄金法则：跑得够快，你才愿意每次改代码都跑一遍。**

### 🟢 GREEN：用边界筑起围墙

```javascript
// src/utils/password.js
const bcrypt = require('bcryptjs');

async function hashPassword(plainPassword) {
  if (!plainPassword || plainPassword.length < 6) {
    throw new Error('密码长度不能少于 6 位');
  }
  const salt = await bcrypt.genSalt(10);
  return bcrypt.hash(plainPassword, salt);
}

async function verifyPassword(plainPassword, hashedPassword) {
  return bcrypt.compare(plainPassword, hashedPassword);
}

module.exports = { hashPassword, verifyPassword };
```

注意第 4 行这个边界检查——**`!plainPassword` 覆盖了 `undefined`、`null`、空字符串三种情况；`length < 6` 覆盖了太短的密码。** 一条语句，挡住了所有非法输入。

没有这条边界，攻击者传个空字符串就能注册、能登录，你的用户数据如同虚设。

**安全问题从来不是"能不能防住黑客"，而是"有没有在最源头拦住问题"。**

再跑一次——

```bash
$ npx jest tests/unit/password.test.js
```

**🟢 全绿。4 条测试，全部通过。**

这就是边界测试带来的安全感——你知道空密码进不来，你知道短密码进不来，你知道 `undefined` 也不会让你的程序崩溃。

---

## 四、RED #3 → GREEN #3：JWT——payload 格式是"前后端的宪法"

JWT 的作用不只是"生成一个 token"那么简单。

它定义了 **payload 里有什么字段**——前端用 `user_id` 来识别用户，移动端用 `user_id` 来缓存会话。

**如果 payload 格式变了，前端就崩了。** 这不是夸张——你真的改过 payload 字段名然后忘了通知前端吗？

JWT 测试的本质是在说：**"后端不能单方面修改 payload 格式。payload 的每个字段，都是前后端的共同约定。"**

### 🔴 RED：把契约写进测试

```javascript
// tests/unit/jwt.test.js
it('签发 token 应使用 user_id（非标准 sub）', () => {
  jwt.sign.mockReturnValue('mock-token');
  const token = signToken(1);
  expect(jwt.sign).toHaveBeenCalledWith(
    { user_id: 1 },   // 注意：是 user_id，不是 sub！
    config.jwt.secret,
    { expiresIn: 86400 }  // 24 小时
  );
});

it('缺少用户 ID 应抛出错误', () => {
  expect(() => signToken()).toThrow('用户 ID 不能为空');
});

it('verifyToken 应返回正确 payload', () => {
  jwt.verify.mockReturnValue({ user_id: 1 });
  const decoded = verifyToken('some-token');
  expect(decoded.user_id).toBe(1);
});
```

跑一下——

```bash
$ npx jest tests/unit/jwt.test.js
```

**💥 红色。文件不存在。** 熟悉的 RED。

但注意这段测试里最微妙的地方：**我们断言了 `{ user_id: 1 }`，而不是 `{ sub: 1 }`。**

为什么用 `user_id` 而不是 JWT 标准的 `sub`？因为 SPEC 就是这么定的。这不是一个技术决策，这是一个**契约决策**——SPEC 说了用 `user_id`，那就必须用 `user_id`。

再看 `expiresIn: 86400`——24 小时，写死的。如果哪天有人把 `config.jwt.expiresIn` 改成了 0（永不过期），这条测试会**立刻**报错，像一记响亮的耳光：

> "你改了 token 过期时间？你确定前后端都知道吗？"

### 🟢 GREEN：把契约写进代码

```javascript
// src/utils/jwt.js
const jwt = require('jsonwebtoken');
const config = require('../config');

function signToken(userId) {
  if (!userId) {
    throw new Error('用户 ID 不能为空');
  }
  return jwt.sign(
    { user_id: userId },
    config.jwt.secret,
    { expiresIn: config.jwt.expiresIn }
  );
}

function verifyToken(token) {
  return jwt.verify(token, config.jwt.secret);
}

module.exports = { signToken, verifyToken };
```

跑测试——

```bash
$ npx jest tests/unit/jwt.test.js
```

**🟢 3 条全绿。**

三行实现代码，三条测试——每一行都有测试在下面撑着。改 `user_id` 为 `sub`？测试报警。改 `expiresIn`？测试报警。忘了 userId 校验？测试报警。

**这就是契约的力量——不是写在文档里让人看，而是写在测试里，让机器自动校验。**

---

## 五、Iter 1 回顾：13 passed，13 total ✅

最后，让我们把三个文件合在一起跑一遍——

```bash
$ npx jest tests/unit/

Test Suites: 3 passed, 3 total
Tests:       13 passed, 13 total
```

**3 个文件，13 条测试，全部通过。**

停下来，感受一下这几个数字意味着什么——

| 模块 | 测试条数 | 覆盖了什么 |
|------|---------|-----------|
| `errors` | 6 | 错误格式、状态码默认值、预定义错误常量 |
| `password` | 4 | 密码长度、空值、undefined、匹配验证 |
| `jwt` | 3 | payload 格式、过期时间、参数校验 |

**13 条测试 = 13 个你不需要手动检查的点。**

你可能会说："才 13 条测试，有啥了不起？"

**了不起的地方不在于数量，而在于过程。**

回想一下：每个文件的第一遍跑都是**红色**的，第二遍跑就**绿**了。这种"从红到绿的爽感"，是 TDD 给你的正反馈循环——你写测试的时候知道自己要什么，写代码的时候知道自己写对了，跑测试的时候知道自己真的写对了。

**每一行代码都有测试在下面撑着，这种感觉，比代码 review 十遍都踏实。**

![](imgs/05/01-tdd-red-green-cycle.svg)

而且你注意到了吗？**整个过程中我们没有 debug 过。** 没有 `console.log`，没有打断点，没有"让我看看这个值是什么"。

因为测试已经把路铺好了——你写代码的时候就知道它是对的，因为测试定义了"什么是对的"。

---

## 六、进入 Iter 2：数据模型来了

Iter 1 搞定，工具函数层稳了。下一步：**数据模型 + 种子数据。**

```
Tests: 13 passed, 13 total ✅
```

---

*下一篇：06-Iter 2——数据模型 + 种子数据。*