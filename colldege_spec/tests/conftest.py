"""公共 fixture — 数据库 session + 测试 token"""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.core.auth.utils import create_access_token, hash_password
from src.core.database import Base


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


_student_counter = [0]


@pytest.fixture
def mock_student_token():
    _student_counter[0] += 1
    return create_access_token(
        sub=f"openid-student-{_student_counter[0]:04d}", role="student"
    )


@pytest.fixture
def mock_admin_token():
    return create_access_token(sub="admin-001", role="admin")


@pytest.fixture
def mock_counselor_token():
    return create_access_token(
        sub="counselor-001",
        role="counselor",
        class_name="2026计算机1班",
        college="计算机学院",
    )


@pytest.fixture
def mock_counselor_token_other_class():
    return create_access_token(
        sub="counselor-002",
        role="counselor",
        class_name="2026计算机2班",
        college="计算机学院",
    )


@pytest.fixture
def seed_data():
    return {
        "admin": {
            "username": "admin",
            "password_hash": hash_password("admin123"),
        },
        "counselor": {
            "username": "counselor01",
            "name": "张老师",
            "college": "计算机学院",
            "class_name": "2026计算机1班",
            "password_hash": hash_password("counselor123"),
        },
    }
