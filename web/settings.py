"""환경 설정."""

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from core.config import DEFAULT_WATERMARK_START_PAGE, PROJECT_ROOT


def _default_temp_root() -> Path:
    if os.name == "nt":
        return PROJECT_ROOT / "tmp" / "pdf_secure"
    return Path("/tmp/pdf_secure")


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_anon_key: str
    supabase_jwt_secret: str
    auth_disabled: bool
    temp_root: Path
    job_retention_seconds: int
    max_upload_bytes: int
    default_watermark_start_page: int
    cleanup_interval_seconds: int
    cookie_secure: bool

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            supabase_url=os.environ.get("SUPABASE_URL", "").rstrip("/"),
            supabase_anon_key=os.environ.get("SUPABASE_ANON_KEY", ""),
            supabase_jwt_secret=os.environ.get("SUPABASE_JWT_SECRET", ""),
            auth_disabled=_env_bool("AUTH_DISABLED", False),
            temp_root=Path(os.environ.get("PDF_SECURE_TEMP_ROOT", str(_default_temp_root()))),
            job_retention_seconds=int(os.environ.get("JOB_RETENTION_SECONDS", "3600")),
            max_upload_bytes=int(os.environ.get("MAX_UPLOAD_BYTES", str(100 * 1024 * 1024))),
            default_watermark_start_page=int(
                os.environ.get(
                    "DEFAULT_WATERMARK_START_PAGE",
                    str(DEFAULT_WATERMARK_START_PAGE),
                )
            ),
            cleanup_interval_seconds=int(os.environ.get("CLEANUP_INTERVAL_SECONDS", "300")),
            cookie_secure=_env_bool("COOKIE_SECURE", False),
        )

    def validate_auth_config(self) -> None:
        if self.auth_disabled:
            return
        missing = []
        if not self.supabase_url:
            missing.append("SUPABASE_URL")
        if not self.supabase_anon_key:
            missing.append("SUPABASE_ANON_KEY")
        if not self.supabase_jwt_secret:
            missing.append("SUPABASE_JWT_SECRET")
        if missing:
            raise RuntimeError(
                f"인증 설정이 필요합니다: {', '.join(missing)} "
                "(로컬 테스트는 AUTH_DISABLED=1)"
            )


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
