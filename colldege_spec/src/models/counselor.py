from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, select
from sqlalchemy.orm import Mapped, mapped_column, Session
from src.core.database import Base


class Counselor(Base):
    __tablename__ = "counselor"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[str] = mapped_column(String(16), default="counselor")
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    college: Mapped[str] = mapped_column(String(64), nullable=False)
    class_name: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    @classmethod
    def find_by_username(cls, db: Session, username: str) -> Optional["Counselor"]:
        return db.execute(
            select(cls).where(cls.username == username)
        ).scalar_one_or_none()
