
from __future__ import annotations
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "colldege-spec"
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24h
    db_path: str = "./data/colldege.db"

    @property
    def mcp_endpoint(self) -> str | None:
        return None

    model_config = {"env_prefix": "COLLEGE_", "case_sensitive": False}


settings = Settings()
