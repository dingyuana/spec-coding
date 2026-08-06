from __future__ import annotations

from datetime import date, datetime
from sqlalchemy.orm import Session
from src.models.student import Student
from src.schemas.registration import RegistrationCreate
from src.utils.errors import AppException


def create_registration(db: Session, schema: RegistrationCreate, openid: str) -> Student:
    existing = Student.find_by_openid(db, openid)
    if existing:
        raise AppException(409, "已提交，请勿重复提交")
    student = Student(
        openid=openid,
        student_id=str(schema.student_id),
        name=schema.name,
        college=schema.college,
        class_name=schema.class_name,
        building=schema.building,
        phone=schema.phone,
        id_number=schema.id_number,
        emergency_contact=schema.emergency_contact,
        emergency_phone=schema.emergency_phone,
        enrollment_date=schema.enrollment_date,
        status="SUBMITTED",
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def get_by_openid(db: Session, openid: str) -> Student | None:
    return Student.find_by_openid(db, openid)


def update_registration(db: Session, schema: RegistrationCreate, openid: str) -> Student:
    student = Student.find_by_openid(db, openid)
    if not student:
        raise AppException(404, "未找到报到记录")
    if student.status != "REJECTED":
        raise AppException(403, "当前状态不允许修改")
    student.student_id = str(schema.student_id)
    student.name = schema.name
    student.college = schema.college
    student.class_name = schema.class_name
    student.building = schema.building
    student.phone = schema.phone
    student.id_number = schema.id_number
    student.emergency_contact = schema.emergency_contact
    student.emergency_phone = schema.emergency_phone
    student.enrollment_date = schema.enrollment_date
    student.status = "SUBMITTED"
    student.reject_reason = ""
    student.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(student)
    return student
