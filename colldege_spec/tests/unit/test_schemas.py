"""单元测试 — Pydantic Schema（报到信息入参校验）"""
import pytest
from src.schemas.registration import RegistrationCreate


class TestRegistrationCreate:
    """校验 Pydantic Schema 的字段约束（STU-S3）"""

    def test_valid_input(self):
        """STU-S1: 合法输入通过校验"""
        schema = RegistrationCreate(
            name="张三",
            student_id="20260001",
            college="计算机学院",
            class_name="2026计算机1班",
            building="A1栋",
            phone="13800138000",
            id_number="110101200001011234",
            emergency_contact="李四",
            emergency_phone="13900139000",
            enrollment_date="2026-09-01",
        )
        assert schema.phone == "13800138000"

    def test_missing_required_field(self):
        """STU-S3: 缺少必填字段 → Validation Error"""
        with pytest.raises(Exception):
            RegistrationCreate(
                name="张三",
                student_id="20260001",
                college="计算机学院",
                class_name="2026计算机1班",
                building="A1栋",
                phone="13800138000",
                id_number="110101200001011234",
                emergency_contact="李四",
                emergency_phone="13900139000",
                # 缺少 enrollment_date
            )

    def test_phone_非11位(self):
        """STU-S3: 手机号非 11 位 → Validation Error"""
        with pytest.raises(Exception):
            RegistrationCreate(
                name="张三",
                student_id="20260001",
                college="计算机学院",
                class_name="2026计算机1班",
                building="A1栋",
                phone="123",
                id_number="110101200001011234",
                emergency_contact="李四",
                emergency_phone="13900139000",
                enrollment_date="2026-09-01",
            )

    def test_id_number_非18位(self):
        """STU-S3: 身份证号非 18 位 → Validation Error"""
        with pytest.raises(Exception):
            RegistrationCreate(
                name="张三",
                student_id="20260001",
                college="计算机学院",
                class_name="2026计算机1班",
                building="A1栋",
                phone="13800138000",
                id_number="123456",
                emergency_contact="李四",
                emergency_phone="13900139000",
                enrollment_date="2026-09-01",
            )

    def test_id_number_含X合法(self):
        """身份证号末位 X 视为合法 18 位"""
        schema = RegistrationCreate(
            name="张三",
            student_id="20260001",
            college="计算机学院",
            class_name="2026计算机1班",
            building="A1栋",
            phone="13800138000",
            id_number="11010120000101123X",
            emergency_contact="李四",
            emergency_phone="13900139000",
            enrollment_date="2026-09-01",
        )
        assert schema.id_number == "11010120000101123X"
