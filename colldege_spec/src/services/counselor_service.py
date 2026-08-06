from __future__ import annotations

from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.models.student import Student
from src.models.audit_log import AuditLog
from src.utils.errors import AppException
from src.utils.common import log as log_audit


def get_class_students(
    db: Session,
    class_name: str,
    page: int = 1,
    size: int = 20,
    status: str = None,
) -> dict[str, Any]:
    stmt = select(Student).where(Student.class_name == class_name)
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
    counselor_class: str,
    actor_type: str = "counselor",
    actor_id: int = 1,
    actor_name: str = "counselor",
    reason: str = None,
) -> None:
    student = db.get(Student, sid)
    if not student:
        raise AppException(404, "学生记录不存在")
    if student.class_name != counselor_class:
        raise AppException(403, "只能审核本班学生")
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


def get_dashboard(db: Session, class_name: str) -> dict[str, Any]:
    all_students = db.execute(
        select(Student).where(Student.class_name == class_name)
    ).scalars().all()
    by_status = {}
    for s in all_students:
        by_status[s.status] = by_status.get(s.status, 0) + 1
    return {
        "class_name": class_name,
        "today_count": len(all_students),
        "total_count": len(all_students),
        "by_status": by_status,
    }
