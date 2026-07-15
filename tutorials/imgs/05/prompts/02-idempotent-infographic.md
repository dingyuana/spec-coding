---
illustration_id: 05-02
type: infographic
style: tech-blue
palette: blue-tech
article: 05-seed-tutorial
position: "它的本质其实是"打破循环依赖"" 段落之后
---

# 幂等性概念 — 跑多少次都一样

## ZONES (3 vertical frames, top to bottom)

Frame 1 — **第一次运行**
- Icon: seed planting
- "admin 用户不存在 → 创建 → ✅"
- Result: user created

Frame 2 — **第二次运行**
- Icon: seed planting again
- "admin 用户已存在 → 跳过 → ✅"
- Result: same state, no error

Frame 3 — **第 N 次运行**
- Icon: seed with infinity symbol
- "检查存在 → 跳过 → ✅"
- Result: exactly the same state

## LABELS
- "幂等性: 跑 1 次和跑 100 次结果一样" in cyan at bottom

## COLORS
- Background: #0a1628
- Checkmarks: #22d3ee (cyan)
- Frames: semi-transparent blue

## ASPECT
16:9