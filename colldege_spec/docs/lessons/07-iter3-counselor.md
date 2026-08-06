# Iter 3：辅导员模块——只能看本班的"有限权限"

> **场景带入 → 发现问题 → 方案迭代 → 原理拆解 → 效果对比 → 情绪升华**

---

## 一、场景带入：两个辅导员，两套数据

张辅导员负责"2026计算机1班"，李辅导员负责"2026计算机2班"。

他们登录系统，都应该看到"查看学生列表"这个功能。但——
- 张辅导员只能看 1 班的学生
- 李辅导员只能看 2 班的学生
- 如果张辅导员用管理员接口，能看到全部学生——这是**越权**

![](imgs/07/01-class-isolation.svg)

## 二、Token 里存 class_name

辅导员登录时，JWT payload 带上班级：

```python
def create_counselor_token():
    return create_access_token(
        sub="counselor01",
        role="counselor",
        class_name="2026计算机1班",
        college="计算机学院"
    )
```

**class_name 存在 token 里**——每次请求都自带"我能看哪个班"。

## 三、审核时的班级校验

```python
# src/services/counselor_service.py
def audit_student(db, sid, action, reason, counselor):
    student = db.query(Student).get(sid)
    if student.class_name != counselor["class_name"]:
        raise AppException(403, "无权操作非本班学生")
    if action == "REJECTED" and not reason:
        raise AppException(400, "驳回需填写原因")
    student.status = action
    db.add(AuditLog(...))
    db.commit()
```

**两行代码，解决越权问题。**

## 四、测试：故意造一个越权场景

```python
# tests/integration/test_counselor.py
def test_越权审核返回403(self, mock_counselor_token, mock_student_token):
    # 用 1 班的辅导员 token，去审核 2 班的学生
    sid = _create_student(mock_student_token, "20262005", "2026计算机2班")
    r = client.post(f"/counselor/audit/{sid}", json={"action": "APPROVED"},
                    headers={"Authorization": f"Bearer {mock_counselor_token}"})
    assert r.status_code == 403
```

**测试比代码先写**——你写一个"故意违规"的测试，它告诉你"越权必须返回 403"。然后你写代码让它通过。

## 五、三件套：查看 + 审核 + 看板

| 功能 | 接口 | 权限 |
|------|------|------|
| 查看本班 | `GET /counselor/students` | 按 class_name 过滤 |
| 审核 | `POST /counselor/audit/{id}` | class_name 必须匹配 |
| 看板 | `GET /counselor/dashboard` | 只统计本班 |

## 六、效果对比

| 场景 | 无权限隔离 | 有权限隔离 |
|------|-----------|-----------|
| 辅导员A看辅导员B的班 | 能看到 | 403 |
| 辅导员A审核B的班 | 能审核 | 403 |
| 驳回不写原因 | 能驳回 | 400 |

## 七、情绪升华

辅导员这个角色的设计哲学是：**能力越大，责任越大；权限越小，风险越小**。

一个辅导员登录进来，系统告诉他"你可以看本班、审核本班、看本班看板"——
**多一个学生不能看，少一个功能不能省。**

这就是"有限权限"的安全边界。
