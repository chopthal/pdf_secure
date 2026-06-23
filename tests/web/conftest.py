"""web 서비스 테스트 공통."""

import pytest

from web.settings import Settings, clear_settings_cache
from web.services.job_store import JobStore


@pytest.fixture(autouse=True)
def reset_settings():
    clear_settings_cache()
    yield
    clear_settings_cache()


@pytest.fixture
def test_settings(tmp_path, monkeypatch) -> Settings:
    monkeypatch.setenv("AUTH_DISABLED", "1")
    monkeypatch.setenv("PDF_SECURE_TEMP_ROOT", str(tmp_path / "pdf_secure"))
    clear_settings_cache()
    return Settings.from_env()


@pytest.fixture
def job_store() -> JobStore:
    store = JobStore()
    yield store
    store.clear()
