from __future__ import annotations

from datetime import date
from pydantic import BaseModel, Field, field_validator


class RegistrationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    student_id: str = Field(..., min_length=1, max_length=20)
    college: str = Field(..., min_length=1, max_length=64)
    class_name: str = Field(..., min_length=1, max_length=64)
    building: str = Field(..., min_length=1, max_length=64)
    phone: str = Field(..., min_length=1, max_length=20)
    id_number: str = Field(..., min_length=1, max_length=18)
    emergency_contact: str = Field(..., min_length=1, max_length=64)
    emergency_phone: str = Field(..., min_length=1, max_length=20)
    enrollment_date: date = Field(..., description="入学日期")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()
        if len(v) != 11 or not v.isdigit():
            raise ValueError("手机号必须是 11 位数字")
        return v

    @field_validator("id_number")
    @classmethod
    def validate_id_number(cls, v: str) -> str:
        v = v.strip()
        if len(v) != 18:
            raise ValueError("身份证号必须是 18 位")
        return v


class RegistrationRead(BaseModel):
    id: int
    openid: str
    student_id: str
    name: str
    college: str
    class_name: str
    building: str
    phone: str
    emergency_contact: str
    emergency_phone: str
    enrollment_date: date
    status: str
    reject_reason: str = ""
