"""单元测试 — CounselorService（COUN-S2~S6）"""
import pytest
from datetime import date
from src.services.counselor_service import get_class_students, audit_student, get_dashboard
from src.models.student import Student
from src.models.counselor import Counselor
from src.utils.errors import AppException


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


def _make_counselor(db, username, class_name, college="计算机学院"):
    c = Counselor(
        username=username, password_hash="$2b$10$test", name="张老师",
        college=college, class_name=class_name, role="counselor",
    )
    db.add(c)
    db.commit()
    return c


class TestGetClassStudents:

    def test_只返回本班学生(self, db_session):
        """COUN-S2: 辅导员只能看到 class_name 匹配的学生"""
        _make_student(db_session, "op-001", "20260001", "张三", "2026计算机1班")
        _make_student(db_session, "op-002", "20260002", "李四", "2026计算机2班")
        _make_counselor(db_session, "counselor01", "2026计算机1班")

        result = get_class_students(db_session, "2026计算机1班", page=1, size=20)
        names = [r["name"] for r in result["items"]]
        assert "张三" in names
        assert "李四" not in names

    def test_按状态筛选(self, db_session):
        """按 status 筛选"""
        _make_student(db_session, "op-001", "20260001", "张三", "2026计算机1班", status="SUBMITTED")
        _make_student(db_session, "op-002", "20260002", "李四", "2026计算机1班", status="APPROVED")

        result = get_class_students(db_session, "2026计算机1班", page=1, size=20, status="APPROVED")
        assert result["total"] == 1


class TestAuditStudent:

    def test_审核通过(self, db_session):
        """COUN-S3: 审核通过 → APPROVED"""
        s = _make_student(db_session, "op-001", "20260001", "张三", "2026计算机1班")
        audit_student(db_session, s.id, "APPROVED", "2026计算机1班", actor_type="counselor")
        s = db_session.query(Student).get(s.id)
        assert s.status == "APPROVED"

    def test_审核驳回(self, db_session):
        """COUN-S4: 驳回 → REJECTED + reject_reason"""
        s = _make_student(db_session, "op-001", "20260001", "张三", "2026计算机1班")
        audit_student(db_session, s.id, "REJECTED", "2026计算机1班",
                      actor_type="counselor", reason="身份证格式错误")
        s = db_session.query(Student).get(s.id)
        assert s.status == "REJECTED"
        assert s.reject_reason == "身份证格式错误"

    def test_越权审核返回403(self, db_session):
        """COUN-S5: 辅导员审核其他班级 → 403"""
        s = _make_student(db_session, "op-001", "20260001", "张三", "2026计算机2班")
        with pytest.raises(AppException) as exc:
            audit_student(db_session, s.id, "APPROVED", "2026计算机1班", actor_type="counselor")
        assert exc.value.status_code == 403

    def test_驳回无reason抛出400(self, db_session):
        """COUN-S5: 驳回无 reason → AppException(400)"""
        s = _make_student(db_session, "op-001", "20260001", "张三", "2026计算机1班")
        with pytest.raises(AppException) as exc:
            audit_student(db_session, s.id, "REJECTED", "2026计算机1班", actor_type="counselor")
        assert exc.value.status_code == 400


class TestDashboard:

    def test_看板返回班级统计(self, db_session):
        """COUN-S6: 返回本班今日/总数/各状态"""
        _make_student(db_session, "op-001", "20260001", "张三", "2026计算机1班", status="APPROVED")
        _make_student(db_session, "op-002", "20260002", "李四", "2026计算机1班", status="SUBMITTED")

        result = get_dashboard(db_session, "2026计算机1班")
        assert result["total_count"] == 2
        assert result["by_status"]["APPROVED"] == 1
        assert result["by_status"]["SUBMITTED"] == 1
        assert "class_name" in result
