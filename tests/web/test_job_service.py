"""Task 2b: job_service·cleanup 단위 테스트."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from pypdf import PdfReader

from tests.conftest import _write_multipage_pdf
from web.models.job import JobStatus
from web.services.cleanup import cleanup_expired_jobs, remove_job_files
from web.services.job_service import (
    JobService,
    JobValidationError,
    build_output_filename,
    build_watermark_text,
    validate_pdf_upload,
)
from web.services.job_store import JobStore


def _pdf_bytes(tmp_path: Path) -> bytes:
    path = tmp_path / "in.pdf"
    _write_multipage_pdf(path, 3)
    return path.read_bytes()


class TestValidation:
    def test_validate_pdf_upload_rejects_non_pdf(self):
        with pytest.raises(JobValidationError, match="유효한 PDF"):
            validate_pdf_upload(b"not-a-pdf", max_bytes=1000)

    def test_build_watermark_text(self):
        text = build_watermark_text("홍길동", "010-1234")
        assert "홍길동" in text
        assert "010-1234" in text

    def test_build_output_filename(self):
        assert build_output_filename("book.pdf", "김철수") == "book_김철수.pdf"


class TestJobService:
    def test_create_and_process_job(self, test_settings, job_store, tmp_path):
        service = JobService(job_store, test_settings)
        content = _pdf_bytes(tmp_path)

        job = service.create_job(
            file_content=content,
            original_filename="book.pdf",
            buyer_name="홍길동",
            buyer_phone="010-9999",
            pdf_password="pass123",
            watermark_start_page=1,
            user_id="user-1",
        )
        assert job.status == JobStatus.PENDING
        assert job.input_path.is_file()

        service.process_job(job.job_id, "pass123", watermark_start_page=1)

        done = service.get_job(job.job_id)
        assert done is not None
        assert done.status == JobStatus.DONE
        assert done.output_path is not None
        assert done.output_path.is_file()

        reader = PdfReader(str(done.output_path))
        reader.decrypt("pass123")
        assert len(reader.pages) == 3

    def test_get_job_returns_none_when_expired(
        self, test_settings, job_store, tmp_path
    ):
        service = JobService(job_store, test_settings)
        job = service.create_job(
            file_content=_pdf_bytes(tmp_path),
            original_filename="a.pdf",
            buyer_name="a",
            buyer_phone="b",
            pdf_password="p",
            watermark_start_page=5,
            user_id=None,
        )
        job_store.update(
            job.job_id,
            expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
        )
        assert service.get_job(job.job_id) is None

    def test_create_job_rejects_empty_name(self, test_settings, job_store, tmp_path):
        service = JobService(job_store, test_settings)
        with pytest.raises(JobValidationError, match="이름"):
            service.create_job(
                file_content=_pdf_bytes(tmp_path),
                original_filename="a.pdf",
                buyer_name="",
                buyer_phone="b",
                pdf_password="p",
                watermark_start_page=5,
                user_id=None,
            )

    def test_create_job_rejects_korean_password(self, test_settings, job_store, tmp_path):
        service = JobService(job_store, test_settings)
        with pytest.raises(JobValidationError, match="한글"):
            service.create_job(
                file_content=_pdf_bytes(tmp_path),
                original_filename="a.pdf",
                buyer_name="홍길동",
                buyer_phone="010",
                pdf_password="비밀번호",
                watermark_start_page=5,
                user_id=None,
            )


class TestCleanup:
    def test_cleanup_expired_jobs_removes_files(self, test_settings, job_store, tmp_path):
        service = JobService(job_store, test_settings)
        job = service.create_job(
            file_content=_pdf_bytes(tmp_path),
            original_filename="a.pdf",
            buyer_name="a",
            buyer_phone="b",
            pdf_password="p",
            watermark_start_page=5,
            user_id=None,
        )
        job_store.update(
            job.job_id,
            expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
        )
        removed = cleanup_expired_jobs(job_store)
        assert job.job_id in removed
        assert not job.work_dir.exists()

    def test_remove_job_files(self, test_settings, job_store, tmp_path):
        service = JobService(job_store, test_settings)
        job = service.create_job(
            file_content=_pdf_bytes(tmp_path),
            original_filename="a.pdf",
            buyer_name="a",
            buyer_phone="b",
            pdf_password="p",
            watermark_start_page=5,
            user_id=None,
        )
        remove_job_files(job)
        assert not job.work_dir.exists()
