# 大学新生报到系统 — 任务清单

> 对应 SPEC.md 中的所有接口，拆解为可独立完成的开发任务。
> 每个任务标注优先级、依赖关系、预估工作量。

---

## 一、任务总览

| 阶段 | 任务数 | 优先级 |
|------|--------|--------|
| Iter 1: 认证模块 | 8 | P0 |
| Iter 2: 报到信息模块 | 9 | P0 |
| Iter 3: 辅导员端模块 | 7 | P0 |
| Iter 4: 管理端模块 | 8 | P0 |
| Iter 5: 地图模块（高德 MCP） | 6 | P1 |
| Iter 6: 集成测试 | 5 | P0 |

**合计：43 个任务**

---

## 二、Iter 1 — 认证模块（P0）

| # | 任务 | 文件 | 依赖 | 测试数 | 预估 |
|---|------|------|------|--------|------|
| T01 | 写 AuthUtils 单元测试 | `tests/unit/test_auth_utils.py` | 无 | 4 | 1h |
| T02 | 实现 AuthUtils | `src/core/auth/utils.py` | T01 | — | 1h |
| T03 | 写 AuthDeps 单元测试 | `tests/unit/test_auth_deps.py` | 无 | 2 | 1h |
| T04 | 实现 AuthDeps（依赖注入） | `src/core/auth/deps.py` | T03 | — | 0.5h |
| T05 | 写认证路由集成测试 | `tests/integration/test_auth.py` | T02, T04 | 4 | 1.5h |
| T06 | 实现学生登录路由 | `src/routers/auth_student.py` | T05 | — | 1h |
| T07 | 实现管理员/辅导员登录路由 | `src/routers/auth_web.py` | T06 | — | 1h |
| T08 | 实现 Admin 和 Counselor 模型 | `src/models/admin.py` | T07 | — | 0.5h |

**Iter 1 验收标准：**
- 微信 code → session_key → JWT token（payload: openid, role=student）
- 管理员登录 → JWT token（payload: user_id, role=admin）
- 辅导员登录 → JWT token（payload: user_id, role=counselor, college, class_name）
- 无效 token → 401
- 用户名不存在和密码错误的消息相同

---

## 三、Iter 2 — 报到信息模块（P0）

| # | 任务 | 文件 | 依赖 | 测试数 | 预估 |
|---|------|------|------|--------|------|
| T09 | 写 Student 模型单元测试 | `tests/unit/test_student_model.py` | 无 | 4 | 1h |
| T10 | 实现 Student 模型 | `src/models/student.py` | T09 | — | 1h |
| T11 | 写 Pydantic Schema 测试 | `tests/unit/test_schemas.py` | 无 | 5 | 1h |
| T12 | 实现 Pydantic Schema（含扩展字段） | `src/schemas/registration.py` | T11 | — | 1h |
| T13 | 写 RegistrationService 单元测试 | `tests/unit/test_registration_service.py` | T10 | 4 | 1.5h |
| T14 | 实现 RegistrationService | `src/services/registration.py` | T13 | — | 1.5h |
| T15 | 写报到路由集成测试 | `tests/integration/test_registration.py` | T14, T02 | 3 | 1h |
| T16 | 实现 POST/GET/PUT 报到路由 | `src/routers/registration.py` | T15 | — | 1h |
| T17 | 实现数据库初始化脚本 | `scripts/init_db.py` | T10, T08 | — | 0.5h |

**Iter 2 验收标准：**
- 学生提交扩展字段（含身份证/紧急联系人/体检信息/入学日期）→ 201
- 重复提交 → 409
- 字段缺失 → 422（身份证 18 位正则 / 手机 11 位正则）
- 未提交时 GET → 404
- REJECTED 状态可修改，其他状态不可

---

## 四、Iter 3 — 辅导员端模块（P0）

| # | 任务 | 文件 | 依赖 | 测试数 | 预估 |
|---|------|------|------|--------|------|
| T18 | 写 Counselor 模型测试 | `tests/unit/test_counselor_model.py` | 无 | 3 | 1h |
| T19 | 实现 Counselor 模型 | `src/models/counselor.py` | T18 | — | 0.5h |
| T20 | 写 CounselorService 测试 | `tests/unit/test_counselor_service.py` | T19, T10 | 5 | 1.5h |
| T21 | 实现 CounselorService | `src/services/counselor.py` | T20 | — | 1.5h |
| T22 | 写辅导员路由集成测试 | `tests/integration/test_counselor.py` | T21, T02 | 3 | 1h |
| T23 | 实现辅导员端到路由 | `src/routers/counselor.py` | T22 | — | 1h |
| T24 | 实现种子数据（预置辅导员） | `scripts/seed.py` | T19 | — | 0.5h |

**Iter 3 验收标准：**
- 辅导员只能查看本班学生列表
- 辅导员只能审核本班学生
- 辅导员查看本班看板（今日/总数/各状态）
- 辅导员审核记录到 AuditLog
- 种子数据幂等

---

## 五、Iter 4 — 管理端模块（P0）

| # | 任务 | 文件 | 依赖 | 测试数 | 预估 |
|---|------|------|------|--------|------|
| T25 | 写 AdminService 测试 | `tests/unit/test_admin_service.py` | T10 | 6 | 2h |
| T26 | 实现 AdminService（审核/导出/看板/日志） | `src/services/admin.py` | T25 | — | 2h |
| T27 | 实现 AuditLog 模型 | `src/models/audit_log.py` | T25 | — | 0.5h |
| T28 | 写管理端路由集成测试 | `tests/integration/test_admin.py` | T26, T02 | 5 | 1.5h |
| T29 | 实现管理端全部路由 | `src/routers/admin.py` | T28 | — | 1.5h |
| T30 | 实现 CSV 导出工具 | `src/utils/csv_export.py` | T26 | — | 0.5h |
| T31 | 实现看板聚合查询 | `src/services/dashboard.py` | T25 | — | 1h |
| T32 | 实现全局异常处理 | `src/utils/errors.py` | 无 | — | 0.5h |

**Iter 4 验收标准：**
- 全局查看/审核学生（跨班级）
- 审核记录到 AuditLog（操作人/时间/IP/详情）
- 导出 CSV（不含密码哈希）
- 看板：今日/总数/各状态/各学院
- 操作日志查询（分页）
- 全局异常统一 `{ "detail": "..." }`

---

## 六、Iter 5 — 地图模块 高德 MCP（P1）

| # | 任务 | 文件 | 依赖 | 测试数 | 预估 |
|---|------|------|------|--------|------|
| T33 | 写 MCP 客户端 mock 测试 | `tests/unit/test_mcp_client.py` | 无 | 4 | 1.5h |
| T34 | 实现 MCP 客户端封装（mock 模式） | `src/core/mcp/client.py` | T33 | — | 1.5h |
| T35 | 写地图服务测试 | `tests/unit/test_map_service.py` | T34 | 3 | 1h |
| T36 | 实现地图服务 | `src/services/map_service.py` | T35 | — | 1h |
| T37 | 写地图路由集成测试 | `tests/integration/test_map.py` | T36, T02 | 3 | 1h |
| T38 | 实现地图路由（nearby/route/buildings） | `src/routers/map.py` | T37 | — | 1h |

**Iter 5 验收标准：**
- 获取校园附近建筑列表（名称/坐标/距离）
- 计算完整步行路线（起点→终点，坐标点数组/步行时间/距离）
- 获取校园建筑列表
- MCP 不可用时返回兜底静态数据 + 日志警告
- MCP 调用 30 秒超时

---

## 七、Iter 6 — 集成测试（P0）

| # | 任务 | 文件 | 依赖 | 测试数 | 预估 |
|---|------|------|------|--------|------|
| T39 | 场景1：微信登录→提交→辅导员审核通过 | `tests/integration/test_e2e_student_counselor.py` | 全部 | 2 | 1h |
| T40 | 场景2：微信登录→提交→辅导员驳回→修改→重新提交 | `tests/integration/test_e2e_reject.py` | 全部 | 2 | 1h |
| T41 | 场景3：管理员导出+操作日志验证 | `tests/integration/test_e2e_export_log.py` | 全部 | 2 | 1h |
| T42 | 场景4：地图导航端到端（校门→食堂→教学楼） | `tests/integration/test_e2e_map.py` | 全部 | 1 | 1h |
| T43 | 场景5：辅导员越权访问其他班级 → 403 | `tests/integration/test_e2e_permission.py` | 全部 | 2 | 1h |

---

## 八、依赖图

```
T01 (auth_utils_test) ──→ T02 (auth_utils)
    │
T03 (auth_deps_test) ───→ T04 (auth_deps)
    │
    ├─→ T05 (auth_test) ──→ T06 (student_login)
    │                          └─→ T07 (admin_login)
    │                                     └─→ T08 (admin_model)
    │
    ├─→ T09 (student_model_test) ──→ T10 (student_model)
    │                                    ├─→ T13 (reg_service_test) ──→ T14 (reg_service)
    │                                    │                                    └─→ T16 (reg_router)
    │                                    └─→ T11 (schema_test) ──→ T12 (schema)
    │
    ├─→ T18 (counselor_model_test) ──→ T19 (counselor_model)
    │                                        └─→ T20 (counselor_service_test) ──→ T21 (counselor_service)
    │                                                                                    └─→ T23 (counselor_router)
    │
    ├─→ T25 (admin_service_test) ──→ T26 (admin_service) + T27 (audit_log_model)
    │                                       └─→ T28 (admin_test) ──→ T29 (admin_router) + T30 (csv) + T31 (dashboard)
    │
    ├─→ T33 (mcp_test) ──→ T34 (mcp_client)
    │                           └─→ T35 (map_test) ──→ T36 (map_service)
    │                                                    └─→ T37 (map_test) ──→ T38 (map_router)
    │
    └─→ T39-T43 (e2e tests)
```

---

## 九、工作量汇总

| 阶段 | 测试 | 实现 | 预估总工时 |
|------|------|------|-----------|
| Iter 1: 认证 | 10 | 3 文件 | 6.5h |
| Iter 2: 报到信息 | 12 | 4 文件 | 7h |
| Iter 3: 辅导员端 | 11 | 3 文件 | 6h |
| Iter 4: 管理端 | 11 | 6 文件 | 9h |
| Iter 5: 地图 MCP | 10 | 4 文件 | 7h |
| Iter 6: 集成 | 9 | 0 文件 | 5h |
| **合计** | **63** | **20 文件** | **40.5h** |

---

## 十、角色-权限矩阵

| 功能 | 学生 | 辅导员 | 管理员 |
|------|------|--------|--------|
| 微信登录 | ✅ | — | — |
| 账号登录 | — | ✅ | ✅ |
| 提交报到 | ✅ | — | — |
| 修改报到 | ✅ | — | — |
| 查看本班 | — | ✅ | — |
| 审核本班 | — | ✅ | — |
| 查看全局 | — | — | ✅ |
| 审核全局 | — | — | ✅ |
| 导出 CSV | — | — | ✅ |
| 操作日志 | — | — | ✅ |
| 看板（本班） | — | ✅ | — |
| 看板（全局） | — | — | ✅ |
| 管理辅导员 | — | — | ✅ |
| 地图导航 | ✅ | ✅ | ✅ |
