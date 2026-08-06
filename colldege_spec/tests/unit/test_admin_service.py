"""单元测试 — AdminService（ADM-S1~S9）"""
import pytest
from datetime import date
from src.services.admin import get_students, audit_student, get_dashboard, get_logs
from src.models.student import Student
from src.models.counselor import Counselor
from src.models.admin import Admin


def _make_student(db, openid, student_id, name, class_name, college="计算机学院",
                  building="A1栋", status="SUBMITTED"):
    s = Student(
        openid=openid, student_id=student_id, name=name, college=college,
        class_name=class_name, building=building, phone="13800138000",
        id_number="110101200001011234", emergency_contact="李四",
        emergency_phone="13900139000", enrollment_date=date(2026, 9, 1),
        status=status,
    )
    db.add(s)
    db.commit()
    return s


class TestGetStudents:

    def test_返回所有学生(self, db_session):
        """ADM-S1: 全局返回所有学生"""
        _make_student(db_session, "op-001", "20260001", "张三", "2026计算机1班")
        _make_student(db_session, "op-002", "20260002", "李四", "2026计算机2班")
        result = get_students(db_session, page=1, size=20)
        assert result["total"] == 2

    def test_按学院筛选(self, db_session):
        """ADM-S2: 按学院筛选"""
        _make_student(db_session, "op-001", "20260001", "张三", "2026计算机1班", college="计算机学院")
        _make_student(db_session, "op-002", "20260002", "李四", "2026经济1班", college="经济学院")
        result = get_students(db_session, page=1, size=20, college="计算机学院")
        assert result["total"] == 1


class TestAuditStudent:

    def test_审核通过记录到日志(self, db_session):
        """ADM-S3: 审核通过 + AuditLog"""
        s = _make_student(db_session, "op-001", "20260001", "张三", "2026计算机1班")
        audit_student(
            db_session, s.id, "APPROVED", actor_type="admin", actor_id=1,
            actor_name="admin",
        )
        assert s.status == "APPROVED"

    def test_审核驳回记录到日志(self, db_session):
        """ADM-S4: 驳回 + AuditLog + reject_reason"""
        s = _make_student(db_session, "op-001", "20260001", "张三", "2026计算机1班")
        audit_student(
            db_session, s.id, "REJECTED", actor_type="admin", actor_id=1,
            actor_name="admin", reason="学号格式错误",
        )
        assert s.status == "REJECTED"
        assert s.reject_reason == "学号格式错误"


class TestDashboard:

    def test_全局看板(self, db_session):
        """ADM-S7: 返回全局统计"""
        _make_student(db_session, "op-001", "20260001", "张三", "2026计算机1班", status="APPROVED")
        _make_student(db_session, "op-002", "20260002", "李四", "2026计算机1班", status="SUBMITTED")
        _make_student(db_session, "op-003", "20260003", "王五", "2026经济1班", college="经济学院", status="REJECTED")

        result = get_dashboard(db_session)
        assert result["total_count"] == 3
        assert result["by_college"]["计算机学院"] == 2
        assert result["by_college"]["经济学院"] == 1


class TestGetLogs:

    def test_返回操作日志(self, db_session):
        """ADM-S8: 操作日志列表"""
        from src.models.audit_log import AuditLog
        log = AuditLog(
            actor_id=1, actor_type="admin", action="approve",
            target_id=1, target_type="student", detail="审核通过",
        )
        db_session.add(log)
        db_session.commit()
        result = get_logs(db_session, page=1, size=20)
        assert result["total"] == 1

    def test_按action筛选(self, db_session):
        """ADM-S8: 按 action 筛选日志"""
        from src.models.audit_log import AuditLog
        db_session.add(AuditLog(actor_id=1, actor_type="admin", action="approve",
                                target_id=1, target_type="student", detail="审核"))
        db_session.add(AuditLog(actor_id=2, actor_type="counselor", action="reject",
                                target_id=1, target_type="student", detail="驳回"))
        db_session.add(AuditLog(actor_id=2, actor_type="counselor", action="reject",
                                target_id=1, target_type="student", detail="驳回"))
        db_session.commit()
        result = get_logs(db_session, page=1, size=20, action="approve")
        assert result["total"] == 1
