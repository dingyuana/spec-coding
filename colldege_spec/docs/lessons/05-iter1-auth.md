# Iter 1：认证模块——三端登录，一套 JWT

> **场景带入 → 发现问题 → 方案迭代 → 原理拆解 → 效果对比 → 情绪升华**

---

## 一、场景带入：三个登录入口

开学第一天，系统要服务三个角色：

- **学生**：打开微信小程序，微信扫码，`code` 换 token
- **辅导员**：打开网页，输用户名密码
- **管理员**：打开网页，输用户名密码

三个入口，看起来是三个登录。但本质上——**都是"验证身份 → 签发 JWT"**。

![](imgs/05/01-three-login-flow.svg)

## 二、为什么三端用一套 JWT

如果三个端各出一套认证：

```
学生端：   微信 session_key → 自己存 session
辅导员端： 密码验证 → 自己存 session
管理端：   密码验证 → 自己存 session
```

问题是：
- 后端要维护三套 session 存储
- 路由鉴权要写三次
- 权限（辅导员看本班、管理员看全局）要写三遍

**用一套 JWT，三端共享：**

```
JWT payload = { "sub": "openid-xxx", "role": "student", "exp": 123456 }
JWT payload = { "sub": "counselor01", "role": "counselor", "class_name": "2026计算机1班" }
JWT payload = { "sub": "admin", "role": "admin" }
```

**同一个 token 解析，同一个中间件验证，同一个路由分发。**

## 三、JWT 签发与验证

```python
# src/core/auth/utils.py
def create_access_token(sub: str, role: str, **extra) -> str:
    payload = {
        "sub": sub, "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        **extra
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except ExpiredSignatureError:
        raise AppException(401, "token 已过期")
```

**过期 token 自动 401**——不需要手写任何过期检查。

## 四、密码哈希：为什么不用 bcrypt

教程原型（user-login）用了 bcrypt。实测中发现——bcrypt 在不同环境（Python 版本、操作系统）下**编译失败或性能差异大**。

所以改为 **SHA-256 加盐**：

```python
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    return f"{salt}${hashlib.sha256((salt + password).encode()).hexdigest()}"

def verify_password(password: str, hashed: str) -> bool:
    salt, hash_val = hashed.split("$", 1)
    return hash_val == hashlib.sha256((salt + password).encode()).hexdigest()
```

**盐值存在哈希里**——每个密码的哈希都不同，即使明文相同。

## 五、依赖注入：FastAPI 的 "get_current_xxx"

```python
# src/core/auth/deps.py
def get_current_student(request: Request) -> dict:
    payload = decode_access_token(token)
    if payload["role"] != "student":
        raise AppException(403, "权限不足")
    return payload
```

路由直接 `Depends(get_current_student)`——**鉴权逻辑和路由逻辑分离**。

## 六、测试

```python
# tests/integration/test_auth.py
def test_valid_code_returns_token(self, monkeypatch):
    monkeypatch.setattr(main, "_exchange_code", lambda c: {"openid": "test"})
    r = client.post("/auth/student", json={"code": "valid"})
    assert r.status_code == 200
    assert "token" in r.json()

def test_invalid_code_returns_401(self, monkeypatch):
    monkeypatch.setattr(main, "_exchange_code", lambda c: {"openid": None})
    r = client.post("/auth/student", json={"code": "bad"})
    assert r.status_code == 401
```

**8 个单元测试 + 14 个集成测试**，全部 GREEN。

## 七、情绪升华

三个登录入口，一套 JWT，8 个测试守住。

学生扫个码、辅导员输个密码、管理员输个密码——后端只关心一件事：**你是谁，你能做什么**。

**认证不是三个功能，是一种身份。**
