# 把任务排成地图——PLAN.md

> **场景带入 → 发现问题 → 方案迭代 → 原理拆解 → 效果对比 → 情绪升华**

---

## 一、你肯定遇到过的问题——"打开项目，CPU 满载"

你斗志满满地打开项目，手指悬在键盘上。

"好，开工！先写登录接口……等等，测试文件建了吗？环境装了哪些依赖来着？数据库模型确定了吗？路由注册了没有？"

大脑开始疯狂上下文切换，像 Chrome 开了 40 个标签页——

**然后你默默拿起手机，刷了五分钟短视频。**

这不是你懒，不是你没执行力。这是你的大脑在罢工抗议。人的工作记忆只有 4 个槽位，而你试图同时调度 15 个前置任务。**大脑是单核处理器，你非要它当 16 核跑——不蓝屏才怪。**

---

## 二、为什么需要规划？从"大脑堆栈"到"任务地图"

### 认知负担：你的大脑不是无限容量的

人的工作记忆（Working Memory）大约只能同时容纳 **4 个信息块**。当你在一个中型项目中同时跟踪：

- 当前要做什么（1 个块）
- 还有哪些前置没做（3-5 个块）
- 哪些已经做完了（2-3 个块）
- 依赖关系对不对（3-4 个块）

你的工作记忆已经溢出了。**多出来的任务被压进"大脑堆栈"——你隐约知道它们存在，但每次弹出都要花时间去回忆上下文。**

### 任务依赖管理：为什么清单不够用？

你振作起来，写下：

```
1. 写登录接口
2. 写测试
3. 搭环境
```

于是你撸起袖子开始干——先写登录接口，发现需要用到 JWT 工具函数，还没写。切到 JWT，发现需要先装 `jsonwebtoken` 包。装包时发现 `package.json` 都不存在。好，去搭脚手架。搭到一半想起来测试还没写……

**你写了一堆事，但这不是计划——这是许愿清单。**

清单和服务器的 `TODO` 注释一样，只能告诉你"有这些事要做"，却完全不管**先做哪个、哪个等哪个、哪个卡住了整个链条**。

真正的差别在这里：

| 维度 | 清单 (TODO List) | 计划 (PLAN) |
|------|------------------|-------------|
| 结构 | 平铺列表，谁先谁后随缘 | 有向无环图，依赖清晰 |
| 时间感 | 只标记"截止日" | 每一步都有前置条件 |
| 卡住时 | 原地死磕或放弃 | 看依赖链，去完成前置任务 |
| 被打断 | 回来一脸懵 | 上一个 ✅ 就是断点 |
| 完成标志 | 全做完才算"搞定" | 每勾一个 ✅ 都有推进感 |

**列清单是记录焦虑，写 PLAN 才是解决问题。**

![](imgs/02/01-task-dependency-flowchart.svg)

---

## 三、本项目的 PLAN.md

打开 `user-login/PLAN.md`（文件路径：`/root/spec-coding/PLAN.md`），项目被清晰地拆成 **6 个迭代（Iter 0 ~ Iter 5）**，每个迭代内部有细粒度的任务拆解。

### 迭代规划总览

```markdown
# 用户登录模块 — PLAN

## 迭代规划

### Iter 0 — 工程基础（无代码）
| 任务 | 产出 |
|------|------|
| SPEC.md | 全局 SPEC（定义所有迭代的范围） |
| PLAN.md | 本文件 |
| AGENT.md | 编码规范 |
| package.json / .env / .gitignore | 脚手架 |
```

```
Iter 0: 工程基础（SPEC / PLAN / AGENT / 脚手架）
  ↓
Iter 1: 工具函数（3 个文件，13 条测试）
  ↓
Iter 2: 数据模型（2 个文件，5 条测试）
  ↓
Iter 3: 服务层（1 个文件，3 条测试）
  ↓
Iter 4: HTTP 接口（5 个文件，8 条测试）
  ↓
Iter 5: 完整验证（30 条测试全部通过）
```

每个 Iter 内部还有更细的拆解，粒度小到你不需要"思考怎么做"，只需要"动手做"：

```markdown
### Iter 1 — 工具函数层（3 个文件）
| 顺序 | 任务 | 说明 |
|------|------|------|
| 1.1 | SPEC: 工具函数 | 定义 errors / password / jwt 接口 |
| 1.2 | 测试: `tests/unit/errors.test.js` | TDD RED |
| 1.3 | 代码: `src/utils/errors.js` | GREEN |
| 1.4 | 测试: `tests/unit/password.test.js` | TDD RED |
| 1.5 | 代码: `src/utils/password.js` | GREEN |
| 1.6 | 测试: `tests/unit/jwt.test.js` | TDD RED |
| 1.7 | 代码: `src/utils/jwt.js` | GREEN |
```

### 每个 Iter 对应的真实文件

**Iter 0 — 工程基础**
- `/root/spec-coding/SPEC.md` — 全局功能契约
- `/root/spec-coding/PLAN.md` — 本文档
- `/root/spec-coding/AGENT.md` — 编码规范门禁
- `/root/spec-coding/package.json` — 依赖管理
- `/root/spec-coding/.env` / `.env.example` / `.gitignore` — 脚手架

**Iter 1 — 工具函数层**
- `/root/spec-coding/src/utils/errors.js` — 自定义错误类
- `/root/spec-coding/src/utils/password.js` — bcrypt 哈希
- `/root/spec-coding/src/utils/jwt.js` — JWT 签发/验证
- 测试文件: `tests/unit/errors.test.js`, `tests/unit/password.test.js`, `tests/unit/jwt.test.js`

**Iter 2 — 数据模型 + 配置**
- `/root/spec-coding/src/config/index.js` — 环境变量配置
- `/root/spec-coding/src/models/user.js` — 用户模型
- `/root/spec-coding/scripts/seed.js` — 种子数据
- 测试文件: `tests/unit/userModel.test.js`

**Iter 3 — 服务层**
- `/root/spec-coding/src/services/authService.js` — 登录业务逻辑
- 测试文件: `tests/unit/authService.test.js`

**Iter 4 — HTTP 接口层**
- `/root/spec-coding/src/middleware/errorHandler.js` — 全局异常处理
- `/root/spec-coding/src/controllers/authController.js` — 控制器
- `/root/spec-coding/src/routes/auth.js` — 路由
- `/root/spec-coding/src/app.js` — 应用工厂
- `/root/spec-coding/src/index.js` — 入口
- 测试文件: `tests/integration/auth.test.js`

**Iter 5 — 完整验证**
- `npm test` 全部通过
- 手动 curl 验证 4 个 Scenario

### 依赖链图

```plaintext
Iter 0（工程基础）
  ↓
Iter 1（工具函数）→ 独立，无项目内依赖
  ↓
Iter 2（模型 + 配置）→ 依赖 Iter 1 的 errors/password
  ↓
Iter 3（服务层）→ 依赖 Iter 1+2
  ↓
Iter 4（控制层）→ 依赖 Iter 3
  ↓
Iter 5（验证）→ 依赖全部
```

### 里程碑

| 里程碑 | 定义 | 条件 |
|--------|------|------|
| M1 | 工具函数全绿 | Iter 1 完成 |
| M2 | 用户模型 + 种子可用 | Iter 2 完成 |
| M3 | 登录业务逻辑测试通过 | Iter 3 完成 |
| M4 | HTTP 接口全部覆盖 | Iter 4 完成 |
| M5 | 25 条测试全部通过 | ✅ 全部完成 |

看到没有？**每一步都有明确的"完成定义"**——测试先写，实现后写，亮了绿灯才算完。依赖关系从 Iter 0 一路流到 Iter 5，不存在"做着做着发现前置没做"的情况。

---

## 四、本质：外挂大脑

我们来算一笔认知账。

**没有 PLAN 时，你的大脑在同时跑 5 个线程：**

- 线程 1：记住所有任务 → "有 30 件事要做……其中 12 件是啥来着？"
- 线程 2：记住依赖关系 → "写接口前是不是该先搭环境？还是先写模型？"
- 线程 3：记住完成状态 → "那个工具函数写完了没？好像是写了……还是没写？"
- 线程 4：上下文切换 → "刚才在写测试，现在切回接口，那段代码到哪了……"
- 线程 5：真正写代码

**五个线程抢一个 CPU，每个都分不到连续时间片，结果是每个任务都慢，每个都容易出错。** 你每切换一次上下文，平均损失 20 分钟的有效注意力。一天切 5 次？两个小时就这么没了。

所以你需要一个"外挂大脑"——把你的工作记忆**卸载到文件里**。

**有 PLAN 时，你的大脑只需要跑 1 个线程：**

1. **看 PLAN** → 找到当前迭代
2. **找第一个 ⬜** → 那就是你要做的事
3. **执行** → 写代码、跑测试
4. **勾 ✅** → 获得一次 dopamine 奖励
5. **回到第 1 步**

就这么简单。不再需要记住进度——PLAN 替你记住了。不再需要纠结先做什么——依赖关系替你画好了。不再需要担心漏掉什么——迭代结构和完成标准替你兜底了。

**把认知负担从你的脑子里卸到文件里，这就是"外挂大脑"。**

![](imgs/02/02-external-brain-infographic.svg)

---

## 五、有 PLAN 和没 PLAN——真实的差距

光说理论不够。来，看看你日常的每一刻：

| 场景 | 没 PLAN | 有 PLAN |
|------|---------|---------|
| **早上开工** | 花 15 分钟回忆"昨天做到哪了"，期间刷了 3 次消息 | 打开 PLAN，第一个 ⬜ 就是今天的起跑线 |
| **被人打断** | 回来盯着屏幕发呆，不知道从哪续上 | 上一个 ✅ 就是断点，看一眼就知道 |
| **任务卡住** | 原地死磕，以为是自己不行 | 看依赖链，发现某个前置任务还没完成 |
| **选任务做** | 凭感觉挑"容易的"或"想做的" | 按 Iter 顺序走，依赖关系说了算 |
| **进度感知** | "感觉做了不少，但又好像没做啥" | 数 ✅ 的数量，每一个勾都是实在的推进 |
| **心理负担** | 30 件事堆在脑子里，焦虑感满格 | 30 件事摊在文件里，每次就看眼前这一个 |

**一句话总结：没 PLAN 时你在跟自己的大脑打架，有 PLAN 时你在跟 PLAN 配合打架——而且 PLAN 永远不会忘事。**

---

## 六、下一迭代

地图画好了，接下来你需要**路标**——告诉你自己和团队，每一步该怎么走、代码写成什么样才算合格。

接下来写**编码规范——AGENT.md**。

---

*下一篇：03-AGENT.md——把规范写成门禁。*