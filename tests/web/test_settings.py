"""Task 1: web/settings 단위 테스트."""

import os

import pytest

from web.settings import Settings, clear_settings_cache, get_settings


@pytest.fixture(autouse=True)
def reset_settings_cache(monkeypatch):
    clear_settings_cache()
    yield
    clear_settings_cache()


class TestSettings:
    def test_default_temp_root_on_windows(self, monkeypatch):
        monkeypatch.delenv("PDF_SECURE_TEMP_ROOT", raising=False)
        monkeypatch.setattr(os, "name", "nt")
        settings = Settings.from_env()
        assert "tmp" in str(settings.temp_root).replace("\\", "/")
        assert settings.job_retention_seconds == 3600
        assert settings.max_upload_bytes == 100 * 1024 * 1024

    def test_auth_disabled_from_env(self, monkeypatch):
        monkeypatch.setenv("AUTH_DISABLED", "true")
        settings = Settings.from_env()
        assert settings.auth_disabled is True

    def test_validate_auth_config_raises_when_incomplete(self):
        settings = Settings(
            supabase_url="",
            supabase_anon_key="",
            supabase_jwt_secret="",
            auth_disabled=False,
            temp_root=Settings.from_env().temp_root,
            job_retention_seconds=3600,
            max_upload_bytes=100,
            default_watermark_start_page=5,
            cleanup_interval_seconds=300,
            cookie_secure=False,
        )
        with pytest.raises(RuntimeError, match="SUPABASE_URL"):
            settings.validate_auth_config()

    def test_validate_auth_config_ok_when_disabled(self):
        settings = Settings(
            supabase_url="",
            supabase_anon_key="",
            supabase_jwt_secret="",
            auth_disabled=True,
            temp_root=Settings.from_env().temp_root,
            job_retention_seconds=3600,
            max_upload_bytes=100,
            default_watermark_start_page=5,
            cleanup_interval_seconds=300,
            cookie_secure=False,
        )
        settings.validate_auth_config()

    def test_cookie_secure_from_env(self, monkeypatch):
        monkeypatch.setenv("COOKIE_SECURE", "true")
        settings = Settings.from_env()
        assert settings.cookie_secure is True

    def test_get_settings_cached(self, monkeypatch):
        monkeypatch.setenv("AUTH_DISABLED", "1")
        assert get_settings() is get_settings()
