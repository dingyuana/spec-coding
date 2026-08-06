from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column, Session
from src.core.database import Base


class Student(Base):
    __tablename__ = "student"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    openid: Mapped[str] = mapped_column(unique=True, nullable=False)
    student_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    college: Mapped[str] = mapped_column(nullable=False)
    class_name: Mapped[str] = mapped_column(nullable=False)
    building: Mapped[str] = mapped_column(nullable=False)
    phone: Mapped[str] = mapped_column(nullable=False)
    id_number: Mapped[str] = mapped_column(nullable=False)
    emergency_contact: Mapped[str] = mapped_column(nullable=False)
    emergency_phone: Mapped[str] = mapped_column(nullable=False)
    health_info: Mapped[str] = mapped_column(default="")
    enrollment_date: Mapped[date] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(default="PENDING")
    reject_reason: Mapped[str] = mapped_column(default="")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def find_by_openid(cls, db: Session, openid: str) -> Optional["Student"]:
        return db.execute(
            select(cls).where(cls.openid == openid)
        ).scalar_one_or_none()

    @classmethod
    def find_by_id(cls, db: Session, student_id: str) -> Optional["Student"]:
        return db.execute(
            select(cls).where(cls.student_id == student_id)
        ).scalar_one_or_none()

    @classmethod
    def find_all(cls, db: Session) -> list["Student"]:
        return db.execute(select(cls)).scalars().all()
