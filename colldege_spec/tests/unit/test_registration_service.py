"""单元测试 — RegistrationService（STU-S1~S7）"""
import pytest
from datetime import date
from src.services.registration import create_registration, get_by_openid, update_registration
from src.schemas.registration import RegistrationCreate
from src.utils.errors import AppException


class TestCreateRegistration:

    def test_首次提交成功(self, db_session):
        """STU-S1: 首次提交返回 SUBMITTED"""
        schema = RegistrationCreate(
            name="张三", student_id="20260001", college="计算机学院",
            class_name="2026计算机1班", building="A1栋", phone="13800138000",
            id_number="110101200001011234", emergency_contact="李四",
            emergency_phone="13900139000", enrollment_date=date(2026, 9, 1),
        )
        student = create_registration(db_session, schema, "openid-001")
        assert student.status == "SUBMITTED"
        assert student.openid == "openid-001"

    def test_重复提交抛出409(self, db_session):
        """STU-S2: 重复提交抛出 AppException(409)"""
        schema = RegistrationCreate(
            name="张三", student_id="20260001", college="计算机学院",
            class_name="2026计算机1班", building="A1栋", phone="13800138000",
            id_number="110101200001011234", emergency_contact="李四",
            emergency_phone="13900139000", enrollment_date=date(2026, 9, 1),
        )
        create_registration(db_session, schema, "openid-001")
        with pytest.raises(AppException) as exc:
            create_registration(db_session, schema, "openid-001")
        assert exc.value.status_code == 409


class TestGetRegistration:

    def test_已提交可查询(self, db_session):
        """STU-S4: GET 返回完整记录"""
        schema = RegistrationCreate(
            name="张三", student_id="20260001", college="计算机学院",
            class_name="2026计算机1班", building="A1栋", phone="13800138000",
            id_number="110101200001011234", emergency_contact="李四",
            emergency_phone="13900139000", enrollment_date=date(2026, 9, 1),
        )
        create_registration(db_session, schema, "openid-001")
        result = get_by_openid(db_session, "openid-001")
        assert result is not None
        assert result.student_id == "20260001"

    def test_未提交返回None(self, db_session):
        """STU-S5: GET 未提交 → None"""
        result = get_by_openid(db_session, "openid-notexist")
        assert result is None


class TestUpdateRegistration:

    def test_REJECTED状态可修改(self, db_session):
        """STU-S6: REJECTED 状态允许修改"""
        schema = RegistrationCreate(
            name="张三", student_id="20260001", college="计算机学院",
            class_name="2026计算机1班", building="A1栋", phone="13800138000",
            id_number="110101200001011234", emergency_contact="李四",
            emergency_phone="13900139000", enrollment_date=date(2026, 9, 1),
        )
        student = create_registration(db_session, schema, "openid-001")
        student.status = "REJECTED"
        student.reject_reason = "测试驳回"
        db_session.commit()

        new_schema = RegistrationCreate(
            name="张三", student_id="20260001", college="计算机学院",
            class_name="2026计算机1班", building="A1栋", phone="13800138000",
            id_number="110101200001011234", emergency_contact="李四",
            emergency_phone="13900139000", enrollment_date=date(2026, 9, 1),
        )
        updated = update_registration(db_session, new_schema, "openid-001")
        assert updated.status == "SUBMITTED"

    def test_SUBMITTED状态不可修改(self, db_session):
        """STU-S7: SUBMITTED 状态修改 → AppException(403)"""
        schema = RegistrationCreate(
            name="张三", student_id="20260001", college="计算机学院",
            class_name="2026计算机1班", building="A1栋", phone="13800138000",
            id_number="110101200001011234", emergency_contact="李四",
            emergency_phone="13900139000", enrollment_date=date(2026, 9, 1),
        )
        create_registration(db_session, schema, "openid-001")
        with pytest.raises(AppException) as exc:
            update_registration(db_session, schema, "openid-001")
        assert exc.value.status_code == 403

    def test_APPROVED状态不可修改(self, db_session):
        """APPROVED 状态也不允许修改"""
        schema = RegistrationCreate(
            name="张三", student_id="20260001", college="计算机学院",
            class_name="2026计算机1班", building="A1栋", phone="13800138000",
            id_number="110101200001011234", emergency_contact="李四",
            emergency_phone="13900139000", enrollment_date=date(2026, 9, 1),
        )
        student = create_registration(db_session, schema, "openid-001")
        student.status = "APPROVED"
        db_session.commit()
        with pytest.raises(AppException):
            update_registration(db_session, schema, "openid-001")
