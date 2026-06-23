"""Task 4: FastAPI API·페이지 통합 테스트."""

import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tests.conftest import _write_multipage_pdf
from web.main import create_app
from web.settings import Settings, clear_settings_cache


@pytest.fixture
def api_client(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTH_DISABLED", "1")
    monkeypatch.setenv("PDF_SECURE_TEMP_ROOT", str(tmp_path / "pdf_secure"))
    clear_settings_cache()
    settings = Settings.from_env()
    client = TestClient(create_app(settings))
    client.post("/auth/login", data={"email": "a@b.com", "password": "x"})
    yield client
    clear_settings_cache()


def _sample_pdf_bytes(tmp_path: Path) -> bytes:
    path = tmp_path / "sample.pdf"
    _write_multipage_pdf(path, 4)
    return path.read_bytes()


class TestPages:
    def test_login_page(self, api_client):
        api_client.cookies.clear()
        res = api_client.get("/login")
        assert res.status_code == 200
        assert "로그인" in res.text

    def test_index_requires_login(self, tmp_path, monkeypatch):
        monkeypatch.setenv("PDF_SECURE_TEMP_ROOT", str(tmp_path / "pdf_secure"))
        clear_settings_cache()
        settings = Settings(
            supabase_url="https://example.supabase.co",
            supabase_anon_key="anon-key",
            supabase_jwt_secret="test-jwt-secret-key-32bytes-min!!",
            auth_disabled=False,
            temp_root=tmp_path / "pdf_secure",
            job_retention_seconds=3600,
            max_upload_bytes=100 * 1024 * 1024,
            default_watermark_start_page=5,
            cleanup_interval_seconds=300,
            cookie_secure=False,
        )
        client = TestClient(create_app(settings))
        res = client.get("/", follow_redirects=False)
        assert res.status_code == 303
        assert res.headers["location"] == "/login"


class TestJobsApi:
    def test_create_and_poll_job(self, api_client, tmp_path):
        pdf = _sample_pdf_bytes(tmp_path)
        res = api_client.post(
            "/api/jobs",
            data={
                "buyer_name": "홍길동",
                "buyer_phone": "010-1234",
                "pdf_password": "secret",
                "watermark_start_page": "1",
            },
            files={"file": ("book.pdf", pdf, "application/pdf")},
        )
        assert res.status_code == 200
        job_id = res.json()["job_id"]

        for _ in range(30):
            status_res = api_client.get(f"/api/jobs/{job_id}")
            assert status_res.status_code == 200
            data = status_res.json()
            if data["status"] in ("done", "failed"):
                break
            time.sleep(0.1)

        assert data["status"] == "done"
        assert data["progress"] == 100

        download = api_client.get(f"/api/jobs/{job_id}/download")
        assert download.status_code == 200
        assert download.headers["content-type"] == "application/pdf"

    def test_download_before_done_returns_409(self, api_client, tmp_path):
        from web.models.job import JobStatus

        pdf = _sample_pdf_bytes(tmp_path)
        res = api_client.post(
            "/api/jobs",
            data={
                "buyer_name": "홍길동",
                "buyer_phone": "010",
                "pdf_password": "secret",
                "watermark_start_page": "1",
            },
            files={"file": ("book.pdf", pdf, "application/pdf")},
        )
        job_id = res.json()["job_id"]
        api_client.app.state.job_store.update(job_id, status=JobStatus.PENDING)
        early = api_client.get(f"/api/jobs/{job_id}/download")
        assert early.status_code == 409

    def test_create_job_validation_error(self, api_client, tmp_path):
        pdf = _sample_pdf_bytes(tmp_path)
        res = api_client.post(
            "/api/jobs",
            data={
                "buyer_name": "   ",
                "buyer_phone": "010",
                "pdf_password": "x",
                "watermark_start_page": "5",
            },
            files={"file": ("book.pdf", pdf, "application/pdf")},
        )
        assert res.status_code == 400

    def test_create_job_rejects_korean_password(self, api_client, tmp_path):
        pdf = _sample_pdf_bytes(tmp_path)
        res = api_client.post(
            "/api/jobs",
            data={
                "buyer_name": "홍길동",
                "buyer_phone": "010",
                "pdf_password": "비밀번호",
                "watermark_start_page": "5",
            },
            files={"file": ("book.pdf", pdf, "application/pdf")},
        )
        assert res.status_code == 400
        assert "한글" in res.json()["detail"]

    def test_job_progress_page(self, api_client, tmp_path):
        pdf = _sample_pdf_bytes(tmp_path)
        create = api_client.post(
            "/api/jobs",
            data={
                "buyer_name": "a",
                "buyer_phone": "b",
                "pdf_password": "p",
                "watermark_start_page": "5",
            },
            files={"file": ("x.pdf", pdf, "application/pdf")},
        )
        job_id = create.json()["job_id"]
        page = api_client.get(f"/jobs/{job_id}")
        assert page.status_code == 200
        assert job_id in page.text
