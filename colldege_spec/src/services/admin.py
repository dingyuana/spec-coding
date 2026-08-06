from __future__ import annotations

from typing import Any
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from src.models.student import Student
from src.models.counselor import Counselor
from src.models.admin import Admin
from src.models.audit_log import AuditLog
from src.utils.errors import AppException
from src.utils.common import PageResponse, log as log_audit
from src.core.auth.utils import verify_password, hash_password


def get_students(
    db: Session,
    page: int = 1,
    size: int = 20,
    college: str = None,
    class_name: str = None,
    status: str = None,
) -> dict[str, Any]:
    stmt = select(Student)
    if college:
        stmt = stmt.where(Student.college == college)
    if class_name:
        stmt = stmt.where(Student.class_name == class_name)
    if status:
        stmt = stmt.where(Student.status == status)
    total = db.execute(stmt).scalars().all()
    offset = (page - 1) * size
    items = total[offset:offset + size]
    return {
        "items": [
            {"id": s.id, "student_id": s.student_id, "name": s.name,
             "college": s.college, "class_name": s.class_name,
             "phone": s.phone, "status": s.status, "reject_reason": s.reject_reason,
             "created_at": str(s.created_at)} for s in items
        ],
        "total": len(total),
        "page": page,
        "size": size,
        "has_more": len(total) > offset + size,
    }


def audit_student(
    db: Session,
    sid: int,
    action: str,
    actor_type: str = "admin",
    actor_id: int = 1,
    actor_name: str = "admin",
    reason: str = None,
) -> None:
    student = db.get(Student, sid)
    if not student:
        raise AppException(404, "学生记录不存在")
    if action == "APPROVED":
        student.status = "APPROVED"
        detail = "审核通过"
    elif action == "REJECTED":
        if not reason:
            raise AppException(400, "驳回必须填写原因")
        student.status = "REJECTED"
        student.reject_reason = reason
        detail = f"审核驳回: {reason}"
    else:
        raise AppException(400, "未知操作")
    db.commit()
    db.refresh(student)
    log_audit(actor_id, actor_type, action.lower(), sid, "student", detail, db, AuditLog)


def get_dashboard(db: Session) -> dict[str, Any]:
    all_students = Student.find_all(db)
    by_status = {}
    by_college = {}
    by_class = {}
    for s in all_students:
        by_status[s.status] = by_status.get(s.status, 0) + 1
        by_college[s.college] = by_college.get(s.college, 0) + 1
        by_class[s.class_name] = by_class.get(s.class_name, 0) + 1
    return {
        "today_count": len(all_students),
        "total_count": len(all_students),
        "by_status": by_status,
        "by_college": by_college,
        "by_class": by_class,
    }


def get_logs(
    db: Session,
    page: int = 1,
    size: int = 20,
    action: str = None,
) -> dict[str, Any]:
    stmt = select(AuditLog)
    if action:
        stmt = stmt.where(AuditLog.action == action)
    total = db.execute(stmt.order_by(AuditLog.created_at.desc())).scalars().all()
    offset = (page - 1) * size
    items = total[offset:offset + size]
    return {
        "items": [
            {"id": l.id, "actor_id": l.actor_id, "actor_type": l.actor_type,
             "action": l.action, "target_id": l.target_id,
             "target_type": l.target_type, "detail": l.detail,
             "created_at": str(l.created_at)} for l in items
        ],
        "total": len(total),
        "page": page,
        "size": size,
        "has_more": len(total) > offset + size,
    }


def add_counselor(
    db: Session,
    username: str,
    password: str,
    name: str,
    college: str,
    class_name: str,
) -> Counselor:
    existing = Counselor.find_by_username(db, username)
    if existing:
        raise AppException(409, "辅导员用户名已存在")
    c = Counselor(
        username=username,
        password_hash=hash_password(password),
        name=name,
        college=college,
        class_name=class_name,
        role="counselor",
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def init_seed_data(db: Session) -> None:
    from src.core.auth.utils import hash_password
    admin = Admin(username="admin", password_hash=hash_password("admin123"), role="admin")
    counselor = Counselor(
        username="counselor01", password_hash=hash_password("counselor123"),
        name="张老师", college="计算机学院", class_name="2026计算机1班", role="counselor",
    )
    db.add(admin)
    db.add(counselor)
    db.commit()
