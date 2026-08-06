from __future__ import annotations

from datetime import datetime
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column, Session
from src.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    actor_id: Mapped[int] = mapped_column(nullable=False)
    actor_type: Mapped[str] = mapped_column(nullable=False)
    action: Mapped[str] = mapped_column(nullable=False)
    target_id: Mapped[int] = mapped_column(nullable=False)
    target_type: Mapped[str] = mapped_column(nullable=False)
    detail: Mapped[str] = mapped_column(default="")
    ip_address: Mapped[str] = mapped_column(default="0.0.0.0")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
