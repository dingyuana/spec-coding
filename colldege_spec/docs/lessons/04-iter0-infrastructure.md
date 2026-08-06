# Iter 0：基础设施——在写业务前先修好路

> **场景带入 → 发现问题 → 方案迭代 → 原理拆解 → 效果对比 → 情绪升华**

---

## 一、场景带入：先修路，再开车

你要造一辆车（业务逻辑），但地面上没有路。

数据库连不上、配置读不到、异常到处飞——这些不是业务，是**基础设施**。如果等写到业务层才发现数据库模型没建好，要回退重写，成本是现在的 5 倍。

所以 Iter 0 不写任何业务代码，只做一件事：**修路**。

## 二、Iter 0 做了 3 件事

### 1. 数据库引擎（src/core/database.py）

```python
from sqlalchemy import create_engine, url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

DB_URL = "sqlite:///"
engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
```

一个 `engine`，一个 `SessionLocal`，一个 `Base`——**所有模型都继承 Base，所有路由都用 SessionLocal。**

![](imgs/04/01-db-architecture.svg)

### 2. 应用配置（src/core/config.py）

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    JWT_SECRET: str = "colldege-dev-secret-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

settings = Settings()
```

**不写死在代码里**——生产环境通过 `.env` 注入。

### 3. 异常类（src/utils/errors.py）

```python
class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)
```

所有业务异常都从 `AppException` 派生——`409 重复`、`403 越权`、`400 驳回无原因`。

## 三、测试也写基础设施

```python
# tests/conftest.py
@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
```

**每个测试都用内存 SQLite**——互不干扰，跑完即销毁。

## 四、Iter 0 的测试

```python
# tests/unit/test_db.py
def test_create_session(db_session):
    assert db_session is not None
```

1 个测试，看似多余——但它保证"测试框架本身能用"，后续 100+ 测试都依赖它。

## 五、效果对比

| 方式 | 写到业务层才发现的问题 | 返工成本 |
|------|---------------------|---------|
| 先写业务 | 数据库没建、配置硬编码、异常不统一 | 高（回退重写） |
| 先修基础设施 | 无 | 低（一蹴而就） |

## 六、情绪升华

修路的人，第一个被踩过去。

但修好路之后，每一辆车都跑在铺好的路上——业务逻辑写得快、改得稳、查得清。

**Iter 0 是投入最低、回报最高的 2 小时。**
