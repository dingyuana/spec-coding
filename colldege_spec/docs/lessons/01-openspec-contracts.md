# OPEN-SPEC 模块契约：用 YAML 把"要做什麼"写死

> **场景带入 → 发现问题 → 方案迭代 → 原理拆解 → 效果对比 → 情绪升华**

---

## 一、场景带入：一次"理解偏差"的返工

需求文档里写着"学生提交报到信息"。

后端写完了，字段：姓名、学号、电话、邮箱。
前端写完了，表单：姓名、学号、电话、邮箱。
两边对接时发现——需求里明明写了"身份证"、"紧急联系人"、"体检信息"。

返工三天。

**根因：需求文档是自然语言，自然语言有歧义。**

## 二、为什么不用 Markdown 写接口契约

Markdown 写接口的常见问题：
1. 格式不统一（有人用表格，有人用列表）
2. 机器无法解析（不能自动 lint、不能生成代码）
3. 改了文档不改代码，文档成为"最不可靠的来源"

![](imgs/01/01-spec-vs-markdown.svg)

## 三、OPEN-SPEC 是什么

OPEN-SPEC 就是 `specs/*.yaml`——**纯 YAML 的模块级契约**。

每个模块一个 YAML，结构固定：

```yaml
# 文件: specs/student.yaml
module: student          # 模块名
name: "学生报到信息模块"
description: "提交 / 查询 / 修改新生报到信息"
owner: "STU-S1~S4"
status: active

entities:
  - name: Student
    fields:
      - name: student_id
        type: string
        unique: true
        description: "学号，唯一标识"
      - name: id_number
        type: string
        pattern: "^\\d{17}[\\dXx]$"
        description: "18位身份证号"

actions:
  - id: STU-S1
    description: "提交报到信息"
    method: POST
    path: /student/registration
    request: RegistrationCreate
    response: Student (201)
    errors:
      - code: 409
        condition: "学号或openid已提交"
```

## 四、为什么用 YAML 而不是 JSON

| 对比项 | YAML | JSON |
|--------|------|------|
| 注释 | ✅ 支持 `#` | ❌ |
| 可读性 | 缩进结构，像清单 | 大括号套大括号 |
| 多行文本 | 自然换行 | 需要转义 |
| 机器解析 | ✅ yaml.load | ✅ json.load |

**YAML = 人能读懂 + 机器能解析。**

## 五、本项目 7 个模块契约

```
specs/
├── auth.yaml          # 三端认证（微信/辅导员/管理员）
├── student.yaml       # 学生报到（14字段，重复409）
├── counselor.yaml     # 辅导员（本班查看/审核/看板）
├── admin.yaml         # 管理端（全局审核/导出/看板/日志）
├── map.yaml           # 校园地图（附近建筑/完整路线）
├── mcp.yaml           # MCP 客户端（连接/降级/重试）
└── _template.yaml     # 模板（规范字段）
```

## 六、写契约的两个原则

**1. 契约一旦写入，不改**

改了契约 = 改了接口 = 所有测试可能失败。
所以——先想清楚再写，写了就不再改（除非真正发现遗漏）。

**2. 一个模块一个文件，不要凑**

7 个文件、每个 30-60 行，比 1 个 400 行的文件好读 10 倍。

## 七、情绪升华：契约就是承诺

写 `auth.yaml` 时，你承诺"三端都用 JWT、学生用 code、管理员用密码"。
写 `student.yaml` 时，你承诺"重复提交 409、驳回可改、已通过不可改"。

**代码是契约的履行，测试是契约的验证。**

当后端写了 200 行、前端写了 300 行，但两边完全不用沟通——
因为 `specs/auth.yaml` 已经把"要什么、返回什么、出错什么"写死了。

这就是契约的力量。
