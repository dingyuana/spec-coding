# 把需求写成契约——SPEC.md

> **场景带入 → 发现问题 → 方案迭代 → 原理拆解 → 效果对比 → 情绪升华**

---

## 一、你肯定遇到过的问题

你问同事："登录接口返回什么格式？"

他说："嗯……我翻一下代码。哦，在第 47 行，返回 `{ token }`。"

你记下了。三天后接口改成了 `{ data: { token } }`，但没人告诉你。

**这不是沟通问题，是没有一份"契约"的问题。**

## 二、最直接的做法：写 README

你在 README 里加了一段：

```markdown
## API
- POST /api/auth/login → 返回 token
```

一周后，代码改了，README 没更新。**问题出在 README 是"描述"，不是"契约"。**

![](imgs/01/02-with-vs-without-spec-comparison.svg)

## 三、所以换一种思路：写 SPEC

SPEC 不是"记录"，它是**合同**。白纸黑字写清楚每一种情况。

打开 `user-login/SPEC.md`，最核心的是**接口规范**：

```
正常登录 → 200 { "token": "..." }
密码错误 → 401 { "error": "用户名或密码错误" }
用户不存在 → 401 { "error": "用户名或密码错误" }（和密码错误一样！）
参数缺失 → 400 { "error": "用户名和密码不能为空" }
```

SPEC 还定义了项目的**5 个迭代**，每个迭代只实现一部分：

```
Iter 1: 工具函数（errors + password + jwt）
Iter 2: 数据模型 + 种子
Iter 3: 服务层
Iter 4: HTTP 接口
Iter 5: 完整验证
```

## 四、SPEC 的本质：可执行的文档

SPEC 里每条约定，最终都会变成一条测试用例：

```javascript
// SPEC 说：用户不存在返回 401
it('用户不存在应返回 401', async () => {
  const res = await request(app).post('/api/auth/login')
    .send({ username: 'ghost', password: 'x' });
  expect(res.status).toBe(401);
});
```

**SPEC 是合约，测试是执法者。** 缺了任何一个，另一个就只是摆设。

![](imgs/01/01-spec-contract-framework.svg)

## 五、有 SPEC 和没 SPEC 的差距

| 场景 | 没 SPEC | 有 SPEC |
|------|---------|---------|
| 新同事加入 | 翻代码问人 | 读 SPEC 就懂 |
| 接口变更 | 口头通知，容易遗漏 | 改 SPEC → 改测试 → 改代码 |
| 验收 | 靠人肉点点点 | 30 条测试跑一遍 |

## 六、下一迭代

SPEC 写好了，接下来把任务排成地图——**写 PLAN.md。**

---

*下一篇：02-PLAN.md——把任务排成地图。*