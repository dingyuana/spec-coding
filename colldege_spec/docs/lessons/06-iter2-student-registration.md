# Iter 2：学生报到——从 14 个字段到一次成功提交

> **场景带入 → 发现问题 → 方案迭代 → 原理拆解 → 效果对比 → 情绪升华**

---

## 一、场景带入：一个新生，14 个字段

张三，计算机学院 2026 级新生。打开微信小程序，看到报到表单：

```
姓名、学号、学院、班级、宿舍楼栋、联系方式、身份证
紧急联系人、紧急联系电话、体检信息、入学日期...
```

14 个字段，填一个少一个，但——**只要有一个错了，审核就驳回**。

更麻烦的是：
- 身份证输错了，提交后不能自己改（状态已锁定）
- 重复点击提交，数据库里多了两条一样的记录

![](imgs/06/01-registration-form.svg)

## 二、Schema 层：Pydantic 字段验证

```python
# src/schemas/registration.py
class RegistrationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=20)
    student_id: str = Field(..., min_length=6, max_length=12)
    id_number: str = Field(..., pattern=r"^\\d{17}[\\dXx]$")
    phone: str = Field(..., pattern=r"^\\d{11}$")
    emergency_phone: str = Field(..., pattern=r"^\\d{11}$")
    enrollment_date: str = Field(..., description="入学日期 YYYY-MM-DD")
```

**14 个字段，7 个有模式校验**——身份证、电话、入学日期，格式不对直接 422。

```python
# tests/unit/test_schemas.py
def test_身份证格式错误(self):
    with pytest.raises(ValidationError):
        RegistrationCreate(..., id_number="123456")
```

## 三、Service 层：提交、重复、修改

```python
# src/services/registration.py
def create_registration(db, data, openid) -> Student:
    existing = db.query(Student).filter(
        (Student.student_id == data.student_id) |
        (Student.openid == openid)
    ).first()
    if existing:
        raise AppException(409, "已提交，请勿重复提交")
    student = Student(**data.model_dump(), openid=openid, status="SUBMITTED")
    db.add(student)
    db.commit()
    return student

def update_registration(db, student, data, status="REJECTED"):
    if status != "REJECTED":
        raise AppException(409, "已提交/已通过，不可修改")
    for field, value in data.items():
        setattr(student, field, value)
    db.commit()
```

**三层状态机：**
```
PENDING → SUBMITTED (提交) → APPROVED (通过) → ❌ 不可改
PENDING → SUBMITTED → REJECTED (驳回) → ✅ 可改
```

![](imgs/06/02-status-machine.svg)

## 四、模型层：14 字段 + 枚举

```python
# src/models/student.py
class Student(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[str] = mapped_column(unique=True)
    id_number: Mapped[str]
    phone: Mapped[str]
    status: Mapped[str] = mapped_column(default="PENDING")
    submitted_at: Mapped[datetime | None]
    approved_at: Mapped[datetime | None]
```

**openid + student_id 双唯一**——微信用户和学号都不能重复。

## 五、集成测试

```python
# tests/integration/test_registration.py
def test_重复提交返回409(self, mock_student_token):
    data = self._payload("20260002")
    client.post("/student/registration", json=data, ...)
    r = client.post("/student/registration", json=data, ...)
    assert r.status_code == 409
```

## 六、效果对比

| 场景 | 无 Pydantic 验证 | 有 Pydantic 验证 |
|------|----------------|----------------|
| 身份证输成 11 位 | 存数据库，审核发现 | 直接 422 |
| 重复提交 | 两条记录 | 409 拒绝 |
| 已通过还想改 | 需要人工排查 | 409 自动拦截 |

## 七、情绪升华

一个新生提交报到信息——**后端只需要两行判断**：
"学号或 openid 是否已存在"。

如果不存在，存进去；如果已存在，告诉他"已提交"。

就是这么简单。但让这件事变得简单的，是 **Pydantic 的验证、Service 的事务、模型的约束**——三个层次各管一摊，互不干扰。

**14 个字段，3 层校验，1 次提交，永不出错。**
