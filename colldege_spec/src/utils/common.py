from __future__ import annotations
import logging
from datetime import datetime, timezone
from pydantic import BaseModel

logger = logging.getLogger("colldege")


def log(actor_id: int, actor_type: str, action: str, target_id: int,
        target_type: str, detail: str, db, audit_log_model) -> None:
    """写入操作日志"""
    log_entry = audit_log_model(
        actor_id=actor_id,
        actor_type=actor_type,
        action=action,
        target_id=target_id,
        target_type=target_type,
        detail=detail,
        ip_address="0.0.0.0",
        created_at=datetime.now(timezone.utc),
    )
    db.add(log_entry)
    db.commit()


class PageResponse(BaseModel):
    items: list
    total: int
    page: int
    size: int
    has_more: bool
