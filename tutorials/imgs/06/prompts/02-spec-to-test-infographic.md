---
illustration_id: 06-02
type: infographic
style: tech-blue
palette: blue-tech
article: 06-tdd-red-tutorial
position: "它的本质其实是"把验收标准变成自动化"" 段落之后
---

# 验收标准 → 自动化

## ZONES (3 layers, vertical cascade)

Top layer — **SPEC (人类可读)**
- Document icon
- Text: "Scenario 2: 密码错误 → 返回 401 { error }"
- Color: #3b82f6

Middle layer — **测试 (机器可执行)**
- Code brackets icon
- Code snippet showing expect() statements
- Text: "expect(res.status).toBe(401)"
- Color: #22d3ee

Bottom layer — **代码 (验证实现)**
- Gear icon
- Text: "ctx.status = 401 / ctx.body = { error }"
- Color: #60a5fa

## ARROWS
- SPEC → 测试 → 代码 (all one direction)
- "自动化守护" label on right side

## ASPECT
16:9