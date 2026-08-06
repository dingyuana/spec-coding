# 大学新生报到系统 — SPEC（全局契约）

> 本文档定义整个项目的完整契约。每个迭代只实现其中一部分。
> 版本：2.0 — 新增辅导员角色、扩展报到字段、完整路线导航、操作日志

---

## 一、系统概述

### 1.1 角色

| 角色 | 终端 | 权限范围 |
|------|------|---------|
| 学生 | 微信小程序 | 登录、填写报到信息、查看报到状态、校园地图导航 |
| 辅导员 | Web 端面 | 登录、查看**本班**学生报到状况、审核本班报到、查看本班看板 |
| 管理员 | Web 端面 | 登录、全局审核、全局导出、全局看板、操作日志、班级管理 |

### 1.2 业务场景

**学生端：**
1. 打开小程序，微信授权登录
2. 填写报到信息（扩展字段：姓名/学号/学院/班级/宿舍/身份证/紧急联系人/体检信息/入学日期/联系方式）
3. 提交后查看报到状态
4. 使用高德地图导航（校门→校园内完整路线）

**辅导员端：**
1. 辅导员账号密码登录 Web 端面
2. 查看本班所有学生报到信息列表
3. 审核本班学生报到（通过/驳回）
4. 查看本班看板（本班报到率、各学院统计）

**管理员端：**
1. 管理员账号密码登录 Web 端面
2. 查看所有学生报到信息列表（全局）
3. 审核报到（全局）
4. 导出 CSV
5. 全局看板
6. 操作日志（谁在什么时候做了什么）
7. 班级管理（分配辅导员）

---

## 二、数据模型

### 2.1 Student（报到记录）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK, auto | 主键 |
| openid | str(64) | not null, unique | 微信 openid |
| student_id | str(20) | not null, unique | 学号 |
| name | str(50) | not null | 姓名 |
| college | str(100) | not null | 学院 |
| class_name | str(50) | not null | 班级 |
| building | str(50) | not null | 宿舍楼栋 |
| phone | str(20) | not null | 联系电话 |
| id_number | str(18) | not null | 身份证号 |
| emergency_contact | str(50) | not null | 紧急联系人 |
| emergency_phone | str(20) | not null | 紧急联系电话 |
| health_info | str(500) | nullable | 体检信息 |
| enrollment_date | date | not null | 入学日期 |
| status | enum | not null, default=PENDING | 报到状态 |
| reject_reason | str(500) | nullable | 驳回原因 |
| created_at | datetime | not null | 创建时间 |
| updated_at | datetime | not null | 更新时间 |

### 2.2 Counselor（辅导员）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK, auto | 主键 |
| username | str(50) | not null, unique | 用户名 |
| password_hash | str(128) | not null | bcrypt 哈希 |
| role | str(20) | not null | counselor |
| name | str(50) | not null | 姓名 |
| college | str(100) | not null | 所属学院 |
| class_name | str(50) | not null | 负责班级 |
| created_at | datetime | not null | 创建时间 |

### 2.3 Admin（管理员）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK, auto | 主键 |
| username | str(50) | not null, unique | 用户名 |
| password_hash | str(128) | not null | bcrypt 哈希 |
| role | str(20) | not null | admin |
| created_at | datetime | not null | 创建时间 |

### 2.4 AuditLog（操作日志）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | int | PK, auto | 主键 |
| actor_id | int | not null | 操作人 ID |
| actor_type | str(20) | not null | admin / counselor |
| action | str(50) | not null | 操作类型（approve/reject/export/view） |
| target_id | int | nullable | 目标对象 ID |
| target_type | str(20) | nullable | student / report |
| detail | str(500) | nullable | 操作详情 |
| ip_address | str(45) | nullable | 操作 IP |
| created_at | datetime | not null | 操作时间 |

### 2.5 Status 枚举

```
PENDING → SUBMITTED → APPROVED
                ↘ REJECTED →（修改后）→ SUBMITTED
```

---

## 三、API 接口

### 3.1 认证

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /auth/student | 微信登录（code 换 token） |
| POST | /auth/admin | 管理员登录 |
| POST | /auth/counselor | 辅导员登录 |

### 3.2 报到信息（学生端）

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /student/registration | 提交报到信息 |
| GET | /student/registration | 查看自己的报到信息 |
| PUT | /student/registration | 修改报到信息 |

### 3.3 辅导员端

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /counselor/students | 查看本班学生报到列表 |
| POST | /counselor/audit/{student_id} | 审核本班学生（通过/驳回） |
| GET | /counselor/dashboard | 本班看板统计 |

### 3.4 管理端

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /admin/students | 查看所有报到列表（分页 + 筛选） |
| POST | /admin/audit/{student_id} | 审核（通过/驳回） |
| GET | /admin/export | 导出 CSV |
| GET | /admin/dashboard | 全局看板数据 |
| GET | /admin/logs | 操作日志 |
| POST | /admin/counselors | 添加/管理辅导员 |

### 3.5 地图（高德 MCP）

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /map/nearby | 获取校园附近建筑列表 |
| GET | /map/route | 计算完整步行路线（校门→目标） |
| GET | /map/buildings | 获取校园建筑列表 |

---

## 四、验收标准

| # | 验收项 | 迭代 |
|---|--------|------|
| 1 | 微信 code 可换取 JWT token | Iter 1 |
| 2 | 管理员密码登录成功 | Iter 1 |
| 3 | 辅导员密码登录成功 | Iter 1 |
| 4 | 无效 token 返回 401 | Iter 1 |
| 5 | 学生提交报到信息成功（含扩展字段） | Iter 2 |
| 6 | 重复提交返回已有记录 | Iter 2 |
| 7 | 字段缺失返回 422 | Iter 2 |
| 8 | 辅导员查看本班报到列表 | Iter 3 |
| 9 | 辅导员审核本班（通过/驳回） | Iter 3 |
| 10 | 辅导员查看本班看板 | Iter 3 |
| 11 | 管理员查看全局报到列表 | Iter 4 |
| 12 | 管理员审核 + 操作日志记录 | Iter 4 |
| 13 | 导出 CSV | Iter 4 |
| 14 | 全局看板返回统计 | Iter 4 |
| 15 | 高德 MCP 获取附近建筑 | Iter 5 |
| 16 | 高德 MCP 完整路线计算 | Iter 5 |
| 17 | MCP 不可用优雅降级 | Iter 5 |
| 18 | 端到端场景测试 | Iter 6 |

---

## 五、各迭代 SPEC

### Iter 1 — 认证

- 微信 code → 调用微信 API 换 session_key → 签发 JWT（payload 含 openid, role=student）
- 管理员 username/password → bcrypt 验证 → 签发 JWT（payload 含 user_id, role=admin）
- 辅导员 username/password → bcrypt 验证 → 签发 JWT（payload 含 user_id, role=counselor, college, class_name）
- 401 响应统一 `{ "detail": "..." }`

### Iter 2 — 报到信息

- POST 提交：Pydantic 校验（含扩展字段：身份证号/紧急联系人/体检信息/入学日期/班级）
- GET 查询：按 openid 查唯一记录
- PUT 修改：仅 REJECTED 状态允许修改
- 扩展字段校验：身份证号 18 位正则，手机号 11 位

### Iter 3 — 辅导员端

- GET 列表：按 role=counselor 的 class_name 过滤，只返回本班
- POST 审核：APPROVED 或 REJECTED（带 reason），记录到 AuditLog
- GET 看板：本班今日报到数/总报到数/各状态计数

### Iter 4 — 管理端

- GET 列表：分页，支持按学院/班级/状态过滤
- POST 审核：APPROVED 或 REJECTED（带 reason），记录到 AuditLog
- GET 导出：流式返回 CSV（不含密码哈希）
- GET 看板：全局今日新增/总数/各状态/各学院
- GET 日志：操作日志列表（分页）
- POST 管理辅导员

### Iter 5 — 地图（高德 MCP）

- 高德 MCP 连接外部地图服务
- nearby：返回校园建筑列表（名称/坐标/距离）
- route：完整步行路线（起点→终点，坐标点数组/步行时间/距离）
- 校园建筑列表（静态 + 高德 POI）
- MCP 不可用时返回兜底静态数据

### Iter 6 — 集成

- 学生登录→提交→辅导员审核（本班）/管理员审核（全局）
- 数据导出验证 + 操作日志验证
- 地图导航端到端（校门→食堂→教学楼）

### Iter 7 — 验证

- 45 条测试全绿
- 需求回溯完整

---

## 六、Non-goals

- 不实现学生注册（只通过微信登录）
- 不实现宿舍自动分配（宿舍楼栋由学生手动选择）
- 不实现短信通知（微信模板消息另行讨论）
- 不实现实时聊天
- 前端代码在 Iter 0 只搭框架，不写页面逻辑
- MCP 使用 mock 模式实现核心逻辑，真实高德连接后续配置
- 不实现多校区配置（单校区）
