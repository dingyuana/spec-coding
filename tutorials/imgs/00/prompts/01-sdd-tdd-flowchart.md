---
illustration_id: 00-01
type: flowchart
style: tech-blue
palette: blue-tech
article: 00-sdd-tdd-intro
position: 第三段 "RED → GREEN → REFACTOR" 之后
---

# SDD+TDD 流水线

## ZONES (3 columns, horizontal flow)

Left column — **SDD** (Spec-Driven Development)
- Icon: document/contract icon
- Label: "写契约" (SPEC.md / PLAN.md / AGENT.md)
- Subtext: "先想清楚"

Middle column — **TDD RED**
- Icon: red X / stop sign
- Label: "先写测试 → 全部失败"
- Subtext: "把验收变成断言"

Right column — **TDD GREEN + REFACTOR**
- Icon: green checkmark
- Label: "写代码 → 全部通过"
- Subtext: "让测试驱动实现"

## FLOW
- Arrows: Left → Middle → Right, all glowing cyan (#22d3ee)
- Bottom: circular arrow from Right back to Middle (REFACTOR loop)

## STYLE
- Background: deep blue gradient #0a1628 → #1a3a6a
- Columns: semi-transparent blue panels with border #3b82f6
- Labels: white #ffffff, subtext in cyan #22d3ee
- Glow effect on arrows

## ASPECT
16:9