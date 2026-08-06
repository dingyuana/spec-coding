from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger("colldege")


class AppException(Exception):
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.message = message

    def to_dict(self) -> dict[str, Any]:
        return {"status_code": self.status_code, "message": self.message}
