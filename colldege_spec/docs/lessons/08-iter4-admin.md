# Iter 4：管理端——全局视野 + 操作可追溯

> **场景带入 → 发现问题 → 方案迭代 → 原理拆解 → 效果对比 → 情绪升华**

---

## 一、场景带入：教务处王老师的三个需求

九月中旬，开学快结束了。教务处王老师坐下来做三件事：

1. **看全局**：全校今天提交了多少、通过多少、哪个学院还没报到
2. **导出数据**：把已审核的学生名单导成 Excel 给学籍科
3. **查记录**：上周张辅导员驳回了 5 个人，具体是谁、什么时间、什么原因

![](imgs/08/01-admin-dashboard.svg)

**三个需求，三个模块：看板、导出、日志。**

## 二、全局看板：一张图看懂全校

```python
# src/services/admin.py
def get_dashboard(db) -> dict:
    students = db.query(Student).all()
    today = datetime.today().strftime("%Y-%m-%d")
    return {
        "today_count": sum(1 for s in students if s.submitted_at
                          and s.submitted_at[:10] == today),
        "total_count": len(students),
        "by_status": {
            "SUBMITTED": sum(1 for s in students if s.status == "SUBMITTED"),
            "APPROVED": sum(1 for s in students if s.status == "APPROVED"),
            "REJECTED": sum(1 for s in students if s.status == "REJECTED"),
        },
        "by_college": {},
    }
```

**5 个数字，一个字典**——前端拿到直接渲染看板。

![](imgs/08/02-dashboard-structure.svg)

## 三、导出 CSV：不用装 pandas

```python
# src/main.py
@app.get("/admin/export")
def export_csv(admin: dict = Depends(get_current_admin)):
    students = get_students(db, ...)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=student_fields)
    writer.writeheader()
    for s in students:
        writer.writerow({
            "学号": s.student_id, "姓名": s.name,
            "学院": s.college, "状态": s.status,
        })
    buffer.seek(0)
    return Response(content=buffer.getvalue(),
                    media_type="text/csv",
                    headers={"Content-Disposition":
                             "attachment; filename=students.csv"})
```

**不用 pandas、不用 openpyxl**——Python 标准库 `csv` + `io.StringIO` 就够了。

## 四、操作日志：每笔审核都留痕

```python
# src/models/audit_log.py
class AuditLog(Base):
    actor_id: Mapped[int]
    actor_type: Mapped[str]       # admin / counselor
    action: Mapped[str]           # approve / reject
    target_id: Mapped[int]
    target_type: Mapped[str]      # student
    detail: Mapped[str | None]
    created_at: Mapped[datetime]
```

**审核通过、驳回、修改——每次操作都写一条日志。**

```python
# 测试
def test_审核写日志(self, db_session):
    audit_student(db_session, sid, "APPROVED", "admin", 1, "admin")
    logs = get_logs(db_session, 1, 20)
    assert logs["total"] == 1
    assert logs["items"][0]["action"] == "APPROVED"
```

## 五、添加辅导员：管理端独有能力

```python
@app.post("/admin/counselors")
def add_counselor(data, admin=Depends(get_current_admin)):
    c = Counselor(username=data.username, name=data.name,
                  password_hash=hash_password(data.password),
                  college=data.college, class_name=data.class_name)
    db.add(c)
    db.commit()
```

**辅导员只能由管理员创建**——辅导员不能自己注册。

## 六、权限矩阵

| 接口 | 辅导员 | 管理员 |
|------|--------|--------|
| GET /counselor/students | ✅ 本班 | — |
| GET /admin/students | ❌ 403 | ✅ 全局 |
| POST /admin/audit | ❌ 403 | ✅ |
| POST /admin/counselors | ❌ 403 | ✅ |

**辅导员访问 `/admin/*` 一律 403**——路由层 `Depends(get_current_admin)` 拦死。

## 七、情绪升华

管理员这个角色的设计哲学是：**全局视野 + 可追溯**。

看板告诉你"发生了什么"，导出帮你"把数据拿出去"，日志告诉你"谁做了什么"。

**一个系统好不好，不看出来的时候快不快，出问题的時候能不能查。**
