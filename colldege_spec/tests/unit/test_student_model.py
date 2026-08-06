"""单元测试 — Student 模型"""
from __future__ import annotations

import pytest
from datetime import date
from sqlalchemy.orm import Session
from src.models.student import Student


class TestStudentModel:

    def test_create_student_所有字段(self, db_session: AsyncSession):
        """STU-S1: 创建完整 Student 记录"""
        student = Student(
            openid="openid-001",
            student_id="20260001",
            name="张三",
            college="计算机学院",
            class_name="2026计算机1班",
            building="A1栋",
            phone="13800138000",
            id_number="110101200001011234",
            emergency_contact="李四",
            emergency_phone="13900139000",
            health_info="无异常",
            enrollment_date=date(2026, 9, 1),
            status="SUBMITTED",
        )
        db_session.add(student)
        db_session.commit()
        assert student.id is not None
        assert student.status == "SUBMITTED"

    def test_openid_唯一约束(self, db_session: AsyncSession):
        """openid 唯一约束"""
        s1 = Student(
            openid="openid-unique",
            student_id="20260001",
            name="张三", college="计算机学院", class_name="2026计算机1班",
            building="A1栋", phone="13800138000", id_number="110101200001011234",
            emergency_contact="李四", emergency_phone="13900139000",
            enrollment_date=date(2026, 9, 1), status="SUBMITTED",
        )
        s2 = Student(
            openid="openid-unique",
            student_id="20260002",
            name="王五", college="计算机学院", class_name="2026计算机1班",
            building="A2栋", phone="13800138001", id_number="110101200001011235",
            emergency_contact="赵六", emergency_phone="13900139001",
            enrollment_date=date(2026, 9, 1), status="SUBMITTED",
        )
        db_session.add(s1)
        db_session.commit()
        db_session.add(s2)
        with pytest.raises(Exception):
            db_session.commit()

    def test_student_id_唯一约束(self, db_session: AsyncSession):
        """student_id 唯一约束"""
        s1 = Student(
            openid="openid-a", student_id="20260001", name="张三",
            college="计算机学院", class_name="2026计算机1班", building="A1栋",
            phone="13800138000", id_number="110101200001011234",
            emergency_contact="李四", emergency_phone="13900139000",
            enrollment_date=date(2026, 9, 1), status="SUBMITTED",
        )
        s2 = Student(
            openid="openid-b", student_id="20260001", name="李四",
            college="计算机学院", class_name="2026计算机1班", building="A2栋",
            phone="13800138001", id_number="110101200001011235",
            emergency_contact="王五", emergency_phone="13900139001",
            enrollment_date=date(2026, 9, 1), status="SUBMITTED",
        )
        db_session.add(s1)
        db_session.commit()
        db_session.add(s2)
        with pytest.raises(Exception):
            db_session.commit()

    def test_default_status_PENDING(self, db_session: AsyncSession):
        """未指定 status 时默认为 PENDING"""
        student = Student(
            openid="openid-default", student_id="20260002",
            name="测试", college="计算机学院", class_name="2026计算机1班",
            building="A1栋", phone="13800138000",
            id_number="110101200001011234", emergency_contact="李四",
            emergency_phone="13900139000", enrollment_date=date(2026, 9, 1),
        )
        db_session.add(student)
        db_session.commit()
        assert student.status == "PENDING"
