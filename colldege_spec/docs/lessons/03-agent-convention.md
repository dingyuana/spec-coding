# AGENT.md：让所有代码看起来像一个人写的

> **场景带入 → 发现问题 → 方案迭代 → 原理拆解 → 效果对比 → 情绪升华**

---

## 一、场景带入：两个人，两种风格

后端开发小A写了这么一段：

```python
def get_student(db, sid):
    q = select(Student).where(Student.student_id == sid)
    r = db.execute(q).scalar()
    return r
```

后端开发小B写了这么一段：

```python
def find_student_record(session, student_id):
    stmt = select(Student).where(Student.student_id == student_id)
    result = session.execute(stmt).first()
    return result
```

**功能一样，风格完全不同。** 三个月后小A离职了，小B来维护——花半天时间搞懂"为什么这里叫 sid，那里叫 student_id"。

## 二、AGENT.md 的三件事

AGENT.md 就是**编码规范**，规定三件事：

### 1. 命名规范

```
文件名：snake_case  （student_model.py）
类名：  PascalCase   （class Student）
函数：  snake_case   （def create_student）
数据库：snake_case   （student_id, enrollment_date）
```

### 2. 分层规范

```
models/   → 只有数据库模型（SQLAlchemy）
schemas/  → 只有请求/响应验证（Pydantic）
services/ → 只有业务逻辑（不碰 HTTP）
routers/  → 只有路由（调用 service，不写逻辑）
```

**Service 层不 import FastAPI，Router 层不 import SQLAlchemy。**

![](imgs/03/01-layer-boundary.svg)

### 3. 错误处理规范

```python
# ❌ 直接抛异常
raise ValueError("学号已存在")

# ✅ 用统一的 AppException
from src.utils.errors import AppException
raise AppException(409, "已提交，请勿重复提交")
```

## 三、为什么用 Pydantic 而不是裸 dict

```python
# ❌ 裸 dict——字段缺失、类型错误、无提示
def create(data: dict):
    name = data["name"]           # Key error？
    phone = data.get("phone")     # 格式对不对？不知道

# ✅ Pydantic——自动验证、错误提示清晰
class RegistrationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=20)
    phone: str = Field(..., pattern=r"^\\d{11}$")
```

Pydantic 的 `model_dump(mode="json")` 还会自动把 `date` 对象转成字符串。

## 四、效果对比

| 场景 | 有 AGENT.md | 无 AGENT.md |
|------|-----------|-----------|
| 新人加入 | 10 分钟看懂代码结构 | 半天摸索 |
| 代码审查 | 检查命名 + 分层即可 | 每个文件风格都不一样 |
| 重构 | 有边界感，知道改哪里 | 改了 models 忘了 schemas |

## 五、情绪升华

AGENT.md 的本质是**消除认知摩擦**。

当你写的代码、同事写的代码、三个月后你自己写的代码，读起来像同一个人写的——
这不是"规范"，这是"尊重"。

**尊重写代码的人，也尊重读代码的人。**
