"""헬스체크 API."""

from fastapi.testclient import TestClient

from web.main import create_app
from web.settings import Settings, clear_settings_cache


def test_health_returns_ok(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTH_DISABLED", "1")
    monkeypatch.setenv("PDF_SECURE_TEMP_ROOT", str(tmp_path / "pdf_secure"))
    clear_settings_cache()
    client = TestClient(create_app(Settings.from_env()))
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
    clear_settings_cache()
