# 成果 02 — PLAN.md：任务看板

> 对应教程：`tutorials/02-plan.md-tutorial.md`  
> 实际文件：`PLAN.md`

---

## 📄 我们写出来的文件

打开 `user-login/PLAN.md`，它像一张"施工进度表"，告诉我们**先做什么、后做什么**。

### 任务分级（P0 最优先）

```
P0 工程基础 → SPEC / PLAN / AGENT / package.json / .env / .gitignore
    ↓
P1 种子数据 → scripts/seed.js（预置 admin 用户）
    ↓
P2 写测试   → tests/unit/*.test.js + tests/integration/auth.test.js
    ↓
P3 写代码   → src/ 全部源码
    ↓
P4 验证     → npm test 全部通过
```

### 为什么要把任务分四级？

```
没有 PLAN：你面前有 20 件事，不知道从哪开始，可能会先做最简单的而不是最重要的
有 PLAN：你只看 P0，P0 做完了再看 P1，一步一步走
```

### 依赖关系（PLAN 告诉你"卡住时怎么办"）

```
如果 P0 没做完（比如 .env 没配置好）
→ P1 的种子脚本跑不起来
→ P2 的测试也跑不起来
→ P3 的代码更没法写
```

> PLAN 不是"任务清单"，它是"不让你卡住的路线图"。

---

下一步 → [成果 03：AGENT.md — 编码规范](results/03-agent-result.md)