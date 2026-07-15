---
illustration_id: 05-01
type: flowchart
style: tech-blue
palette: blue-tech
article: 05-seed-tutorial
position: "所以我們换一种思路：写一个种子脚本" 之后
---

# 打破循环依赖

## ZONES (2 states, side by side)

Left side — **循环依赖** (Circular Dependency)
- Circular arrows: "注册" → "登录" → "需要用户" → "需要注册" → ...
- Red warning signs on each node
- Text: "鸡生蛋 蛋生鸡"
- Colors: red/orange frustration

Right side — **种子打破循环** (Seed Breaks the Chain)
- Straight line: "种子脚本" → "预置 admin 用户" → "登录接口直接可用" → "测试无需等注册"
- Green checkmarks
- Arrow breaks through the circle
- Colors: cyan/green success

## CENTER
- Breaking arrow cutting through the circular chain

## ASPECT
16:9