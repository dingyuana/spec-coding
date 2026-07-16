# 第4章：让 Agent 先写测试——红色是故事的起点

> **写给准备把指挥棒交给 Agent 的你**：上一章，我们写了一整份 Spec.md，把需求翻译成了一份没有歧义的“合同”。你可能觉得意犹未尽，但也可能有点怀疑：“这玩意儿真的有用吗？Agent 真能读懂？”
>
> 本章，我们就来做一次历史性的交接：**你不再敲键盘写测试，而是对 Agent 说一句话，然后看着它为你生成一片红色的测试海洋。** 你将从“码农”正式升级为“指挥官”。坐稳，我们要发指令了。

---

## 4.1 指令的艺术：怎么对 Agent 说话？

你可能会想：“我就跟 Agent 说‘帮我写测试’不就行了？”但如果真的这么模糊，Agent 会陷入两难：写什么功能的测试？覆盖哪些场景？用什么框架？边界条件测不测？

还记得我们在第 2 章创建的 `Task.md` 吗？那份文件就是用来解决这个问题的。在 Task.md 的第二阶段，我们已经列出了 5 条具体的测试子任务。所以，我们对 Agent 发出的第一条正式指令应该是：

> **“Agent，请读取 `docs/Spec.md`，确认状态为 `approved`。然后读取 `Task.md`，执行第二阶段 TDD-Red 的所有子任务：编写全部测试代码，但不写任何实现代码。”**

这句话包含了三个关键信息：
1. **依据**：Spec.md（需求真相来源）
2. **范围**：Task.md 第二阶段（只做测试，不做实现）
3. **约束**：不写实现代码（确保红灯）

Agent 收到后，会按以下流程自动操作：
1. 读取 Spec.md，解析所有输入约束、错误码、边界条件
2. 读取 Task.md，确认当前进度
3. 生成 `test_register.py`，包含所有测试函数
4. 运行 `pytest`，确认全部红灯
5. 更新 `Task.md` 第二阶段状态

---

## 4.2 Agent 的输出：一份完整的测试套件

下面，就是 Agent 在接收到我们指令后，自动生成并写入 `test_register.py` 的完整代码。**这份代码不是人写的，是 Agent 根据 Spec.md 逐条翻译出来的。** 我们要逐段审查，看看它是不是真的理解了我们的“合同”。

### 4.2.1 导入与测试夹具

```python
# test_register.py
"""用户注册功能测试套件。

本文件由 Agent 根据 docs/Spec.md 自动生成。
每个测试函数的 docstring 标注了对应的规格条目。
"""

import os
import pytest
from register import register, UserRepository
from database import init_db, get_connection, DB_PATH


@pytest.fixture(autouse=True)
def setup_database():
    """每个测试用例执行前后，自动重建全新的空数据库。
    
    保证测试隔离性：任何测试都可以独立运行，互不干扰。
    """
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
    yield
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
```

> **人类审查点评**：Agent 正确使用了 `autouse=True` 的 fixture，确保每个测试都在干净的数据库上运行。这是我们在 SystemPrompt.md 里约定好的。✅

### 4.2.2 成功路径测试

```python
@pytest.mark.success_path
def test_register_success():
    """T1 - 对应 Spec.md「成功响应」
    
    验证：
    1. 合法邮箱 + 合法密码 → 返回字典
    2. 字典包含 userId 和 email
    3. email 为小写形式
    4. 数据库中密码为 bcrypt 哈希（以 $2b$ 开头）
    """
    repo = UserRepository()
    result = register("student@university.edu", "SecurePass123", repo)
    
    assert isinstance(result, dict), "返回值必须是字典"
    assert "userId" in result, "必须包含 userId"
    assert "email" in result, "必须包含 email"
    assert result["email"] == "student@university.edu"
    
    # 验证密码存储安全性（对应业务规则第1条）
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password_hash FROM users WHERE email = ?",
        ("student@university.edu",)
    )
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None, "用户必须已存入数据库"
    assert row["password_hash"] != "SecurePass123", "禁止明文存储密码"
    assert row["password_hash"].startswith("$2b$"), "必须使用 bcrypt 哈希"
```

> **人类审查点评**：Agent 不仅测试了返回值结构，还主动去数据库里验证了密码是 bcrypt 哈希。这是 Spec.md 业务规则第 1 条的体现。Agent 读懂了“禁止明文存储”。✅

### 4.2.3 邮箱校验测试（参数化）

```python
@pytest.mark.email_validation
@pytest.mark.parametrize("email, password, expected_error, description", [
    ("notanemail", "ValidPass1", "INVALID_EMAIL_FORMAT", "缺少 @ 符号"),
    ("", "ValidPass1", "INVALID_EMAIL_FORMAT", "空字符串"),
    ("a" * 256 + "@example.com", "ValidPass1", "INVALID_EMAIL_FORMAT", "超过 255 字符"),
])
def test_register_invalid_email(email, password, expected_error, description):
    """T2 - 对应 Spec.md「INVALID_EMAIL_FORMAT」和边界条件 B2
    
    验证：任何不符合邮箱格式的输入都会抛出 ValueError，
    且错误信息中包含正确错误码。
    """
    repo = UserRepository()
    with pytest.raises(ValueError, match=expected_error):
        register(email, password, repo)
```

> **人类审查点评**：Agent 使用了 `parametrize`，一条测试函数覆盖了三个非法邮箱场景。第二个用例（空字符串）对应 Spec.md 非法示例里的 `""`，第三个（256 字符）对应边界条件 B2。Agent 完全按照 Spec 翻译。✅

### 4.2.4 密码校验测试（参数化）

```python
@pytest.mark.password_validation
@pytest.mark.parametrize("email, password, expected_error, description", [
    ("short@test.com", "Abc1234", "PASSWORD_TOO_SHORT", "7 位密码 < 8"),
    ("long@test.com", "A" * 65 + "1", "PASSWORD_TOO_LONG", "65 位密码 > 64"),
    ("nodigit@test.com", "abcdefgh", "WEAK_PASSWORD", "纯字母无数字"),
    ("noletter@test.com", "12345678", "WEAK_PASSWORD", "纯数字无字母"),
])
def test_register_invalid_password(email, password, expected_error, description):
    """T3 - 对应 Spec.md「PASSWORD_TOO_SHORT / TOO_LONG / WEAK_PASSWORD」
    
    验证：所有非法密码都会抛出对应的 ValueError。
    """
    repo = UserRepository()
    with pytest.raises(ValueError, match=expected_error):
        register(email, password, repo)
```

> **人类审查点评**：密码校验的四个违规类型全覆盖。`"Abc1234"` 刚好 7 位，`"A"*65 + "1"` 刚好 65 位，精确打在边界上。Agent 没有遗漏任何一个错误码。✅

### 4.2.5 密码边界值测试（参数化）

```python
@pytest.mark.password_validation
@pytest.mark.parametrize("email, password, description", [
    ("border8@test.com", "Abcdefg1", "密码刚好 8 位（最小合法长度）"),
    ("border64@test.com", "A" * 63 + "1", "密码刚好 64 位（最大合法长度）"),
    ("space@test.com", "Valid 1 Password", "密码包含空格（合法字符）"),
])
def test_register_valid_password_boundaries(email, password, description):
    """T4 - 对应 Spec.md 边界条件 B3/B4/B5
    
    验证：刚好在合法边界上的密码能够注册成功。
    """
    repo = UserRepository()
    result = register(email, password, repo)
    assert "userId" in result, f"边界测试失败: {description}"
```

> **人类审查点评**：Agent 专门为边界值写了正面测试。`"Abcdefg1"` 刚好 8 位，`"A"*63 + "1"` 刚好 64 位，`"Valid 1 Password"` 含空格。这三个场景分别对应 Spec.md 的 B3、B4、B5。Agent 在告诉我们：“我读懂了边界表。” ✅

### 4.2.6 邮箱边界测试

```python
@pytest.mark.email_validation
def test_register_email_exactly_255_chars():
    """T5 - 对应 Spec.md 边界条件 B1
    
    验证：邮箱长度刚好 255 字符可以注册成功。
    """
    local_part = "a" * (255 - len("@example.com"))
    email = local_part + "@example.com"
    repo = UserRepository()
    
    result = register(email, "ValidPass1", repo)
    
    assert result["email"] == email.lower()
```

> **人类审查点评**：Agent 动态构造了刚好 255 字符的邮箱。`255 - len("@example.com")` 计算出 local_part 长度，精确到个位数。这是边界测试的专业写法。✅

### 4.2.7 重复注册测试

```python
@pytest.mark.duplicate_check
def test_register_duplicate_email():
    """T6 - 对应 Spec.md「EMAIL_ALREADY_REGISTERED」和边界条件 B7/B8
    
    验证：
    1. 第一次注册成功
    2. 第二次用同一邮箱（大小写可能不同）注册时抛出异常
    """
    repo = UserRepository()
    email = "duplicate@example.com"
    
    register(email, "SecurePass123", repo)
    
    with pytest.raises(ValueError, match="EMAIL_ALREADY_REGISTERED"):
        register(email, "AnotherPass1", repo)


@pytest.mark.duplicate_check
def test_register_duplicate_email_case_insensitive():
    """T6 补充 - 对应 Spec.md 边界条件 B8
    
    验证：大小写不同的同一邮箱视为重复。
    """
    repo = UserRepository()
    
    register("User@Example.com", "SecurePass123", repo)
    
    with pytest.raises(ValueError, match="EMAIL_ALREADY_REGISTERED"):
        register("user@example.com", "AnotherPass1", repo)
```

> **人类审查点评**：Agent 不仅写了基础重复测试，还额外生成了大小写不敏感的重复测试。这对应 Spec.md 边界条件 B8（“大小写不同视为同一邮箱”）。Agent 展示了对业务规则的深层理解。✅

### 4.2.8 邮箱规范化测试

```python
@pytest.mark.normalization
def test_register_email_normalization():
    """T7 - 对应 Spec.md 边界条件 B6
    
    验证：输入含首尾空格和大写字母时，返回的 email 被规范化为小写且无空格。
    """
    repo = UserRepository()
    
    result = register("  User@Example.com  ", "SecurePass123", repo)
    
    assert result["email"] == "user@example.com"


@pytest.mark.normalization
def test_register_email_already_lowercase():
    """T7 补充 - 验证已小写邮箱不会被错误修改"""
    repo = UserRepository()
    email = "already_lowercase@example.com"
    
    result = register(email, "ValidPass1", repo)
    
    assert result["email"] == email
```

> **人类审查点评**：Agent 还贴心地写了一个“已小写邮箱不被篡改”的补充测试。这是防御性测试，确保规范化逻辑对已规范输入是幂等的。这是一个有经验的程序员才会写的测试。✅

---

## 4.3 运行测试：欣赏一片壮丽的红色

现在，我们把 Agent 生成的 `test_register.py` 保存到项目目录，然后在终端运行：

```bash
pytest test_register.py -v
```

你会看到：

```
test_register.py::test_register_success                              FAILED [  9%]
test_register.py::test_register_invalid_email[缺少 @ 符号]            FAILED [ 18%]
test_register.py::test_register_invalid_email[空字符串]               FAILED [ 27%]
test_register.py::test_register_invalid_email[超过 255 字符]          FAILED [ 36%]
test_register.py::test_register_invalid_password[7 位密码 < 8]        FAILED [ 45%]
test_register.py::test_register_invalid_password[65 位密码 > 64]      FAILED [ 54%]
test_register.py::test_register_invalid_password[纯字母无数字]        FAILED [ 63%]
test_register.py::test_register_invalid_password[纯数字无字母]        FAILED [ 72%]
test_register.py::test_register_valid_password_boundaries[8位]        FAILED [ 81%]
test_register.py::test_register_valid_password_boundaries[64位]       FAILED [ 90%]
test_register.py::test_register_valid_password_boundaries[空格]       FAILED [100%]
test_register.py::test_register_email_exactly_255_chars               FAILED [100%]
test_register.py::test_register_duplicate_email                       FAILED [100%]
test_register.py::test_register_duplicate_email_case_insensitive      FAILED [100%]
test_register.py::test_register_email_normalization                   FAILED [100%]
test_register.py::test_register_email_already_lowercase               FAILED [100%]

========================= 15 failed in 0.15s =========================
```

**15 个测试，15 个失败。** 这在 Agent 驱动的 TDD 里，是最光荣的输出。它不是在骂你，而是在告诉你：

- “你写的 Spec.md，我已经完全理解了。”
- “我把每一条需求都翻译成了对应的测试断言。”
- “现在 `register` 函数还是个空壳，全部红灯完全符合预期。”
- “请确认这些测试是否符合你的预期。如果确认，我将开始 TDD-Green 阶段。”

---

## 4.4 人类审查：读懂 Agent 生成的测试

在让 Agent 继续写实现代码之前，你需要做一件至关重要的事：**审查这些测试是否真的反映了你的需求。** 如果测试写错了，Agent 后面生成的代码也会跟着错。这叫“Garbage in, garbage out”。

你需要逐条确认：

| 检查项 | 你的审查动作 |
|--------|------------|
| 错误码是否正确？ | 看 `match="..."` 里的字符串是否和 Spec.md 完全一致 |
| 边界值是否正确？ | 看参数化数据里的长度、字符是否精确打在边界上 |
| 是否遗漏了某个场景？ | 对着 Spec.md 逐条打勾 |
| 是否有过度测试？ | 有没有测 Spec 里没写的东西？有的话可能是 Agent “脑补”的，要删掉 |
| 测试名字是否清晰？ | 名字应该说明场景，不看 docstring 也能猜出在测什么 |

如果一切都没问题，你可以对 Agent 说：

> **“审查通过。请继续 Task.md 第三阶段：TDD-Green。用最少的代码让所有测试变绿。”**

---

## 4.5 为什么是 Agent 写测试，而不是人写？

你可能会问：“写测试好像也不难，为什么要让 Agent 写？”

答案有三个：

1. **速度快**：你写 15 个测试需要 30 分钟，Agent 只需要 30 秒。而且它不会拼错错误码，不会漏掉边界。
2. **翻译精准**：Agent 是把 Spec.md 的每一行直接“编译”成测试。你手工写可能会遗漏某个参数化分支，Agent 不会——它是逐格扫描的。
3. **格式统一**：Agent 生成的测试风格一致，标记完整，docstring 规范。如果你和三个队友各自手写，风格会五花八门。

但有一件事 Agent 做不到：**判断 Spec 本身对不对。** 如果 Spec.md 里把错误码写成了 `INVALID_EMAIL` 而不是 `INVALID_EMAIL_FORMAT`，Agent 会忠实地在测试里用 `INVALID_EMAIL`——它不会质疑你。所以，**审查是人类的最后一道防线。**

---

## 本章小结

这一章，我们完成了一次历史性的交接：

- **你对 Agent 发出了第一条正式开发指令**，基于 Spec.md 和 Task.md
- **Agent 自动生成了 15 个 pytest 测试**，覆盖了成功路径、所有错误码、所有边界条件、所有业务规则
- **你运行了这些测试，看到了一片壮丽的红色**——证明测试是“活”的、有期待的
- **你做了人类审查**，确认测试完全符合 Spec.md，没有遗漏也没有脑补

现在，你的项目里有了第一份 Agent 生成的代码：`test_register.py`。它像 15 个哨兵一样站在那里，等着拦截任何不满足 Spec.md 的实现代码。你的角色已经从“写代码的人”变成了“审代码的人”。这个转变，会随着课程的深入越来越明显。

> **口诀时刻**：  
> **Spec 是图纸 Agent 读，测试自动生成出；**  
> **红灯一片不怕惧，那是故事的开篇曲。**

下一章，我们将对 Agent 发出第二条指令：“现在，用最少的代码，让这些测试全部变绿。”你会看到 Agent 像一个外科医生一样，一针一线地写出刚好通过测试的实现代码。你，只需要在旁边喝咖啡，看着它干活。准备进入 TDD-Green 阶段了吗？

---
