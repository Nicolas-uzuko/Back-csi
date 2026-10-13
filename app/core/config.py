import json
from functools import lru_cache
from typing import Any, List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://csi_user:csi_password@localhost:5432/csi_sakaraha"

    # Initial Admin
    first_admin_email: str = "randriantinanicolas@gmail.com"
    first_admin_username: str = "admin"
    first_admin_password: str = "Admin12345!"
    first_admin_nom: str = "RANDRIANTINANICOLAS"
    first_admin_prenom: Optional[str] = None
    first_admin_matricule: Optional[str] = "ADMIN-001"

    # Security
    secret_key: str = "development-only-change-this-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    reset_token_expire_minutes: int = 30

    # Storage
    private_storage_path: str = "./private_storage"
    max_upload_size_mb: int = 10

    # Optional SMTP configuration. Password-reset requests stay generic when
    # SMTP is not configured, and the clear token is never logged or returned.
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from: str = "no-reply@localhost"
    reset_email_base_url: str = "http://localhost:3000/reset-password"

    # CORS
    allowed_origins: List[str] = ["http://localhost:3000"]

    # Environment
    environment: str = "development"

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                return json.loads(v)
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000"]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
