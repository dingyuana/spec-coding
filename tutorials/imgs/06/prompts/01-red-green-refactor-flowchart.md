---
illustration_id: 06-01
type: flowchart
style: tech-blue
palette: blue-tech
article: 06-tdd-red-tutorial
position: "所以我們换一种思路：先写测试" 段落之后
---

# RED-GREEN-REFACTOR 循环

## ZONES (3 connected circles, triangular loop)

Circle 1 — **RED** (left)
- Color: red #ef4444
- Icon: X mark
- Label: "写失败的测试"
- Subtext: "25 条测试 → 25 条红色"

Circle 2 — **GREEN** (right)
- Color: green #22c55e
- Icon: checkmark
- Label: "写最少的代码"
- Subtext: "让测试通过"

Circle 3 — **REFACTOR** (bottom)
- Color: blue #3b82f6
- Icon: arrows circling
- Label: "优化代码"
- Subtext: "测试保持绿色"

## FLOW
- Circular arrows connecting all three
- Direction: RED → GREEN → REFACTOR → (back to) RED

## ASPECT
16:9