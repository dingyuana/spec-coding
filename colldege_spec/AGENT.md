# AGENT — 编码规范（FastAPI / Python）

> 本项目编码规范约束。所有开发者（包括 AI）必须遵守。

---

## 一、命名规范

| 类型 | 风格 | 示例 |
|------|------|------|
| 类名 | PascalCase | `class StudentSchema:` |
| 函数/方法 | snake_case | `def get_current_user(...)` |
| 变量 | snake_case | `session_key = ...` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRIES = 3` |
| 文件/目录 | snake_case | `registration.py`, `auth/` |
| 数据库表 | snake_case | `students`, `map_buildings` |
| API 路径 | kebab-case | `/student/registration` |
| JWT 字段 | snake_case | `user_id`, `role` |

---

## 二、分层架构

```
routers/*.py   → 接收请求，参数校验（Pydantic），调用 service，返回 HTTP 响应
       ↓
services/*.py  → 纯业务逻辑，不感知 HTTP，可独立测试
       ↓
models/*.py    → SQLAlchemy 模型，数据库表定义
       ↓
schemas/*.py   → Pydantic schema（请求入参 / 响应出参）
       ↓
core/*.py      → 核心配置、认证、依赖注入、MCP 客户端
       ↓
utils/*.py     → 纯工具函数（加密、日期格式化等）
```

**禁止：**
- routes 直接操作数据库
- service 返回 HTTP Response（返回数据对象）
- router 做业务逻辑判断
- 跨层调用（如 schema 调 service）

---

## 三、依赖注入

FastAPI 依赖注入通过 `Depends()` 实现：

```python
# core/auth/deps.py
async def get_current_student(db: AsyncSession = Depends(get_db)):
    """从 JWT 中获取当前学生（微信端）"""
    ...

async def get_current_admin(db: AsyncSession = Depends(get_db)):
    """从 JWT 中获取当前管理员（Web 端）"""
    ...
```

- 所有需要认证的路由必须注入对应依赖
- 不允许在 router 层手动解析 token

---

## 四、异常处理

使用自定义异常类 + 全局异常处理器：

```python
# utils/errors.py
class AppException(HTTPException):
    def __init__(self, status_code: int, message: str):
        self.message = message
        super().__init__(status_code=status_code, detail=message)
```

- 统一 `{ "detail": "错误消息" }` 响应格式（FastAPI 原生）
- 不允许在 router 中写 `try/except` 吞异常
- 全局 `@app.exception_handler(Exception)` 兜底返回 500

---

## 五、数据库

- 使用 SQLAlchemy 2.0 async 模式
- 数据库文件 `app.db` 不在 Git 中（.gitignore）
- 初始化脚本 `scripts/init_db.py` 创建所有表
- 种子数据脚本 `scripts/seed.py` 预置管理员用户
- **禁止 `SELECT *`**：显式指定字段或使用 ORM 属性

---

## 六、安全规则

| 规则 | 实现 |
|------|------|
| 密码 bcrypt 加密 | `passlib[bcrypt]`，rounds=10 |
| JWT 24h 过期 | 从 .env 读取 `JWT_EXPIRES_IN` |
| 微信 code 换 session_key | 通过微信 API，session_key 不落库明文 |
| 密钥从环境变量读取 | `python-dotenv`，.env 不入 Git |
| 敏感信息不写日志 | 禁止 log openid/session_key |
| 管理员密码不硬编码 | .env 或首次运行生成 |

---

## 七、测试规范

- 框架：pytest + httpx（异步测试）
- Mock 策略：用 `monkeypatch` 或 `mocker`（pytest-mock）
- 覆盖率：`pytest-cov`，阈值 80%
- 每个模块有对应的测试文件
- 集成测试覆盖完整 HTTP 请求链路

---

## 八、代码风格

| 工具 | 配置 |
|------|------|
| ruff | 行宽 88，禁止 `except: pass` |
| mypy | strict mode，所有公共函数有类型注解 |
| Black | 隐式（通过 ruff 格式化） |

---

## 九、文档要求

- 所有公共函数/方法必须有 docstring
- docstring 格式：Google style

```python
async def create_registration(
    schema: RegistrationCreate,
    openid: str,
    db: AsyncSession,
) -> Student:
    """提交学生报到信息。

    Args:
        schema: 报到信息入参
        openid: 当前学生微信 openid
        db: 数据库 session

    Returns:
        创建后的 Student 对象

    Raises:
        AppException: 已有报到记录时抛出
    """
```

---

## 十、MCP 客户端规范

- MCP 连接配置从 .env 读取（endpoint / headers）
- MCP 不可用时优雅降级：返回静态兜底数据 + 日志警告
- MCP 调用必须有 timeout（30 秒）
- 禁止在 MCP 客户端中硬编码地图数据

---

## 十一、前端规范（简要）

### 微信小程序（student 端）
- 页面结构：pages/ 目录下按模块分
- 数据请求：统一 `utils/request.js`，自动携带 token
- token 存储：wx.setStorageSync

### Vue 3（admin 端）
- 使用 Composition API（`<script setup>`）
- 状态管理：Pinia
- HTTP 客户端：axios，拦截器自动加 Authorization header
- 路由守卫：token 校验

---

## 十二、Git 规范

- 分支：`develop`（开发）/ `main`（发布）
- 提交格式：`type: 简短描述（≤50字）`
- 类型：`feat / fix / docs / refactor / perf / test / chore`
- **禁止提交**：.env、app.db、node_modules、__pycache__

---

## 十三、Non-goals

- 不实现短信通知
- 不实现宿舍自动分配
- 不实现实时聊天
- MCP 使用 mock 模式实现核心逻辑，真实连接后续配置
