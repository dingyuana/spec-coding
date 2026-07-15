---
illustration_id: 02-01
type: flowchart
style: tech-blue
palette: blue-tech
article: 02-plan-tutorial
position: "所以我們换一种思路：写 PLAN" 之后
---

# 任务依赖地图

## ZONES (4 horizontal lanes, top to bottom)

Lane 1 — **P0 工程基础**
- Nodes: "SPEC.md" → "PLAN.md" → "AGENT.md" → "package.json"
- All marked ✓ (completed)
- Color: green-tinted blue

Lane 2 — **P1 种子数据**
- Node: "scripts/seed.js"
- Arrow from P0 completion
- Color: cyan #22d3ee

Lane 3 — **P2 TDD**
- Nodes: "写测试用例" → "单元测试" → "集成测试"
- Arrows showing dependency chain

Lane 4 — **P3 实现 + P4 验证**
- Node: "src/" → "npm test"

## CONNECTIONS
- Vertical dotted lines showing dependency: P0 → P1 → P2 → P3/P4
- Only one task active at a time (WIP=1)

## ASPECT
16:9