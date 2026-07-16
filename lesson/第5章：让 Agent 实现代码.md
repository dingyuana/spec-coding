# 第5章：让 Agent 实现代码——最少的代码，最大的信心

> **写给刚看完一片红灯的你**：上一章结束的时候，你的屏幕上是一片壮丽的红色——15 个测试，15 个失败。如果你是一个人战斗，现在应该开始撸袖子写实现了。但今天，你有一个 AI 搭档。你只需要对它说一句话，然后看着它一行一行地写出刚好让测试通过的代码。本章，你将第一次体验“指挥官”的快感：**你下命令，Agent 写代码，测试从红变绿。**

---

## 5.1 对 Agent 下达第二条指令

回顾一下我们的 Task.md，第三阶段是 TDD-Green，包含 6 条子任务：

```markdown
### ⬜ 第三阶段: TDD-Green（最小实现）
- [ ] 实现邮箱格式校验逻辑
- [ ] 实现密码强度校验逻辑
- [ ] 实现重复注册检查逻辑
- [ ] 实现邮箱规范化逻辑
- [ ] 实现 bcrypt 密码哈希
- [ ] 实现 UUID v4 用户 ID 生成
```

所以，我们对 Agent 的指令是：

> **“Agent，测试已审查通过。请执行 Task.md 第三阶段 TDD-Green：编写 `register.py` 的最小实现，让 `test_register.py` 中全部 15 个测试变绿。记住：只写刚好通过测试的代码，不过度设计。”**

---

## 5.2 Agent 的工作过程：逐步让红灯变绿

Agent 收到指令后，不会一次性把所有代码写出来然后碰运气。它会遵循 TDD 的节奏，**一个测试一个测试地让灯变绿**。以下是 Agent 的“思考过程”（由 Agent 自动记录在 Task.md 的进度日志中）：

### 第一步：让 `test_register_success` 变绿

Agent 读取测试，看到它期望 `register()` 返回一个包含 `userId` 和 `email` 的字典。**最简实现**是什么？

```python
# register.py（第一版：只让成功测试变绿）
def register(email: str, password: str, repo=None):
    return {
        "userId": "fake-uuid-for-now",
        "email": email.lower()
    }
```

Agent 运行 `pytest test_register.py::test_register_success -v`，看到绿灯。然后立即运行全部测试，确认：
- ✅ `test_register_success` 绿了
- ❌ 其他 14 个仍然是红（符合预期，因为它们测的是异常场景）

### 第二步：让邮箱校验测试变绿

Agent 看到 `test_register_invalid_email` 期望抛出 `ValueError("INVALID_EMAIL_FORMAT")`。它在函数开头加入邮箱校验：

```python
# register.py（第二版：加入邮箱校验）
def register(email: str, password: str, repo=None):
    normalized_email = email.strip().lower()
    
    if "@" not in normalized_email or len(normalized_email) > 255:
        raise ValueError("INVALID_EMAIL_FORMAT")
    
    return {
        "userId": "fake-uuid-for-now",
        "email": normalized_email
    }
```

运行测试：
- ✅ 成功测试仍然绿
- ✅ 三个邮箱校验测试变绿
- ❌ 密码相关测试仍然红

### 第三步：让密码校验测试变绿

Agent 加入密码长度和强度校验：

```python
import re

def register(email: str, password: str, repo=None):
    normalized_email = email.strip().lower()
    
    if "@" not in normalized_email or len(normalized_email) > 255:
        raise ValueError("INVALID_EMAIL_FORMAT")
    
    if len(password) < 8:
        raise ValueError("PASSWORD_TOO_SHORT")
    if len(password) > 64:
        raise ValueError("PASSWORD_TOO_LONG")
    if not re.search(r"[a-zA-Z]", password):
        raise ValueError("WEAK_PASSWORD")
    if not re.search(r"[0-9]", password):
        raise ValueError("WEAK_PASSWORD")
    
    return {
        "userId": "fake-uuid-for-now",
        "email": normalized_email
    }
```

运行测试：
- ✅ 四个密码异常测试变绿
- ✅ 三个密码边界测试也变绿（它们本来就是合法密码）

### 第四步：让重复注册测试变绿

Agent 需要“记住”哪些邮箱已经注册过。它引入一个简单的集合作为临时存储：

```python
import re

# 临时存储（后面会替换为数据库）
_registered_emails = set()

def register(email: str, password: str, repo=None):
    normalized_email = email.strip().lower()
    
    if "@" not in normalized_email or len(normalized_email) > 255:
        raise ValueError("INVALID_EMAIL_FORMAT")
    
    if len(password) < 8:
        raise ValueError("PASSWORD_TOO_SHORT")
    if len(password) > 64:
        raise ValueError("PASSWORD_TOO_LONG")
    if not re.search(r"[a-zA-Z]", password):
        raise ValueError("WEAK_PASSWORD")
    if not re.search(r"[0-9]", password):
        raise ValueError("WEAK_PASSWORD")
    
    if normalized_email in _registered_emails:
        raise ValueError("EMAIL_ALREADY_REGISTERED")
    
    _registered_emails.add(normalized_email)
    return {
        "userId": "fake-uuid-for-now",
        "email": normalized_email
    }
```

运行测试：
- ✅ `test_register_duplicate_email` 变绿
- ✅ `test_register_duplicate_email_case_insensitive` 也绿了（因为规范化后大小写统一）
- ✅ `test_register_email_normalization` 绿了（去空格+转小写已在第一步实现）
- ✅ `test_register_email_already_lowercase` 绿了
- ✅ `test_register_email_exactly_255_chars` 绿了

**全部 15 个测试，绿色！**

---

## 5.3 Agent 的最终产出：完整的 `register.py`

以下是 Agent 完成 TDD-Green 阶段后，写入 `register.py` 的最终版本：

```python
# register.py
"""用户注册核心业务逻辑模块。

本模块由 Agent 根据 docs/Spec.md 和 test_register.py 自动生成。
遵循 TDD 原则：只写刚好通过测试的最简代码。
"""

import re
import uuid
import bcrypt
from database import get_connection


# ============================================================
# 常量定义（从 Spec.md 提取）
# ============================================================

EMAIL_MAX_LENGTH = 255
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 64

# 错误码（与 Spec.md「失败响应」表格严格一致）
ERR_INVALID_EMAIL_FORMAT = "INVALID_EMAIL_FORMAT"
ERR_PASSWORD_TOO_SHORT = "PASSWORD_TOO_SHORT"
ERR_PASSWORD_TOO_LONG = "PASSWORD_TOO_LONG"
ERR_WEAK_PASSWORD = "WEAK_PASSWORD"
ERR_EMAIL_ALREADY_REGISTERED = "EMAIL_ALREADY_REGISTERED"


# ============================================================
# 数据仓库层（对应 Spec.md 业务规则第 4/5 条）
# ============================================================

class UserRepository:
    """用户数据存储，基于 SQLite 数据库。
    
    负责用户数据的持久化操作。
    """
    
    def exists(self, email: str) -> bool:
        """检查邮箱是否已注册。"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE email = ?",
            (email,)
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def save(self, email: str, password_hash: str, user_id: str) -> None:
        """保存新用户到数据库。"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (id, email, password_hash) VALUES (?, ?, ?)",
            (user_id, email, password_hash)
        )
        conn.commit()
        conn.close()


# ============================================================
# 私有校验函数（从 register 中提取，单一职责）
# ============================================================

def _validate_email(email: str) -> str:
    """校验邮箱格式，返回规范化后的邮箱。
    
    对应 Spec.md「email 约束」第 1-4 条。
    """
    normalized = email.strip().lower()
    if "@" not in normalized or len(normalized) > EMAIL_MAX_LENGTH:
        raise ValueError(ERR_INVALID_EMAIL_FORMAT)
    return normalized


def _validate_password(password: str) -> None:
    """校验密码规则。
    
    对应 Spec.md「password 约束」第 1-3 条。
    """
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(ERR_PASSWORD_TOO_SHORT)
    if len(password) > PASSWORD_MAX_LENGTH:
        raise ValueError(ERR_PASSWORD_TOO_LONG)
    if not re.search(r"[a-zA-Z]", password):
        raise ValueError(ERR_WEAK_PASSWORD)
    if not re.search(r"[0-9]", password):
        raise ValueError(ERR_WEAK_PASSWORD)


def _hash_password(password: str) -> str:
    """对密码进行 bcrypt 哈希。
    
    对应 Spec.md 业务规则第 1 条。
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


# ============================================================
# 核心业务函数
# ============================================================

def register(email: str, password: str, repo: UserRepository = None) -> dict:
    """用户注册。
    
    完整流程（按 Spec.md 定义）：
    1. 校验并规范化邮箱
    2. 校验密码强度
    3. 检查邮箱是否已被注册
    4. 生成 UUID + bcrypt 哈希
    5. 保存到数据库
    6. 返回 userId 和 email
    
    Args:
        email: 用户提供的邮箱地址
        password: 用户提供的密码
        repo: UserRepository 实例（依赖注入，便于测试）
        
    Returns:
        dict: {"userId": "uuid", "email": "normalized@example.com"}
        
    Raises:
        ValueError: 当输入不满足规则时，错误信息为对应的错误码
    """
    if repo is None:
        repo = UserRepository()
    
    normalized_email = _validate_email(email)
    _validate_password(password)
    
    if repo.exists(normalized_email):
        raise ValueError(ERR_EMAIL_ALREADY_REGISTERED)
    
    user_id = str(uuid.uuid4())
    password_hash = _hash_password(password)
    
    repo.save(normalized_email, password_hash, user_id)
    
    return {
        "userId": user_id,
        "email": normalized_email
    }
```

---

## 5.4 运行测试：见证全绿时刻

在终端运行：

```bash
pytest test_register.py -v
```

你会看到：

```
test_register.py::test_register_success                              PASSED [  6%]
test_register.py::test_register_invalid_email[缺少 @ 符号]            PASSED [ 12%]
test_register.py::test_register_invalid_email[空字符串]               PASSED [ 18%]
test_register.py::test_register_invalid_email[超过 255 字符]          PASSED [ 25%]
test_register.py::test_register_invalid_password[7 位密码 < 8]        PASSED [ 31%]
test_register.py::test_register_invalid_password[65 位密码 > 64]      PASSED [ 37%]
test_register.py::test_register_invalid_password[纯字母无数字]        PASSED [ 43%]
test_register.py::test_register_invalid_password[纯数字无字母]        PASSED [ 50%]
test_register.py::test_register_valid_password_boundaries[8位]        PASSED [ 56%]
test_register.py::test_register_valid_password_boundaries[64位]       PASSED [ 62%]
test_register.py::test_register_valid_password_boundaries[空格]       PASSED [ 68%]
test_register.py::test_register_email_exactly_255_chars               PASSED [ 75%]
test_register.py::test_register_duplicate_email                       PASSED [ 81%]
test_register.py::test_register_duplicate_email_case_insensitive      PASSED [ 87%]
test_register.py::test_register_email_normalization                   PASSED [ 93%]
test_register.py::test_register_email_already_lowercase               PASSED [100%]

========================= 15 passed in 0.12s =========================
```

**15 个测试，全部绿色。** 从一片红到一片绿，Agent 用了不到 3 分钟。而你，只做了一件事：**审查 Agent 生成的代码是否符合你的预期。**

---

## 5.5 Green 阶段的铁律：Agent 替你遵守

在传统 TDD 中，Green 阶段有三个铁律。Agent 因为被 Agent.md 约束，会自动遵守：

| 铁律 | Agent 的行为 |
|------|------------|
| **别过度设计** | Agent 只会写刚好通过测试的代码，不会多加任何逻辑 |
| **别预测未来需求** | Spec.md 里没写的，Agent 绝对不会加 |
| **保持短循环** | Agent 每改几行就跑一次测试，确保不破坏已有绿色 |

这就是 Agent 驱动的 TDD 最迷人的地方：**Agent 天生就是 TDD 的最佳实践者。** 它没有“我觉得这样写更好”的冲动，没有“先写个复杂的留着备用”的习惯。它只会忠实地、机械地、精确地——**让测试变绿。**

---

## 5.6 人类审查：Agent 写的代码够好吗？

在进入下一阶段之前，你需要审查 Agent 的产出。以下是审查清单：

| 审查项 | 检查内容 | 结果 |
|--------|---------|------|
| 错误码一致性 | `register.py` 中的错误码字符串是否与 Spec.md 完全一致？ | ✅ |
| 边界值处理 | 邮箱 255 字符、密码 8/64 位的边界是否正确？ | ✅ |
| 密码存储 | 是否使用了 bcrypt？数据库中是否为哈希值？ | ✅ |
| 用户 ID | 是否使用了 UUID v4？ | ✅ |
| 邮箱规范化 | 是否去除了首尾空格并转小写？ | ✅ |
| 重复注册 | 大小写不同的同一邮箱是否被正确拦截？ | ✅ |
| 代码风格 | 是否符合 SystemPrompt.md 的约定？ | ✅ |

如果你对某处不满意，可以对 Agent 说：“请把 `_validate_password` 中的正则匹配改为先编译再使用，提高性能。”Agent 会在重构阶段处理。

---

## 5.7 Task.md 更新

Agent 完成任务后，会自动更新 Task.md：

```markdown
### ✅ 第三阶段: TDD-Green（最小实现）
- [x] 实现邮箱格式校验逻辑
- [x] 实现密码强度校验逻辑
- [x] 实现重复注册检查逻辑
- [x] 实现邮箱规范化逻辑
- [x] 实现 bcrypt 密码哈希
- [x] 实现 UUID v4 用户 ID 生成

### ⬜ 第四阶段: TDD-Refactor（重构优化）
- [ ] 提取常量和错误码
- [ ] 拆分校验辅助函数
- [ ] 引入 UserRepository 数据仓库层
```

你可能会注意到：Agent 在 Green 阶段就已经做了一些重构（提取常量、拆分函数、引入 UserRepository）。这是因为我们的 Spec.md 和 Agent.md 写得太好了——Agent 在“最小实现”阶段就自然地向良好架构靠拢。

但在严格 TDD 中，第四阶段是专门留给重构的。所以下一章，Agent 会检查代码中是否还有需要优化的地方。

---

## 本章小结

- **你发出了一条指令**，Agent 自动完成了 TDD-Green 阶段。
- **Agent 逐测试变绿**：先从最简单的成功路径开始，然后逐步加入校验、查重、哈希。
- **最终产出**：`register.py`，150 行结构清晰、测试全绿的代码。
- **你做了人类审查**，确认代码符合 Spec.md 和编码规范。
- **Task.md 自动更新**，进度一目了然。

> **口诀时刻**：  
> **指令一句话，Agent 写实现；**  
> **红灯逐个灭，全绿心才定。**

下一章，我们要做一件非常重要的事：**让 Agent 补全边界测试，织密安全网。** 现在这 15 个测试看起来已经很全面了，但 Spec.md 里还有一些边界条件我们没测到。我们将对 Agent 说：“根据 Spec.md 的边界条件表，检查测试覆盖是否完整，补全任何遗漏的测试。”你准备好了吗？

---

（新版第 5 章完）