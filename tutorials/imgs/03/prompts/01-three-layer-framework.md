---
illustration_id: 03-01
type: framework
style: tech-blue
palette: blue-tech
article: 03-agent-tutorial
position: "所以我們换一种思路：写 AGENT" 之后
---

# 三层约束模型

## ZONES (3 concentric layers)

Outer layer — **命名层** (Naming)
- Text: "camelCase / PascalCase / UPPER_SNAKE_CASE"
- Color: muted blue #1a3a6a
- Width: thin border

Middle layer — **架构层** (Architecture)
- Text: "routes → controllers → services → models"
- Arrow showing one-way dependency
- Color: medium blue #3b82f6

Inner core — **安全层** (Security)
- Text: "禁止密码明文 / 禁止密钥硬编码 / 防枚举攻击"
- Red/alert colored items
- Color: bright cyan #22d3ee with glow
- This is the most important layer

## LABELS
- Each layer labeled with icon and layer name
- Inner core has warning icon

## ASPECT
16:9