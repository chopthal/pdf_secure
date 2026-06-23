"""PDF 작업 생성·처리."""

import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from core.password import PdfPasswordValidationError, validate_pdf_password
from core.watermark import add_watermark
from web.models.job import Job, JobStatus
from web.services.cleanup import ensure_temp_root, remove_job_files
from web.services.job_store import JobStore
from web.settings import Settings


class JobValidationError(ValueError):
    pass


def validate_pdf_upload(content: bytes, max_bytes: int) -> None:
    if not content:
        raise JobValidationError("PDF 파일이 비어 있습니다.")
    if len(content) > max_bytes:
        raise JobValidationError(f"파일 크기는 {max_bytes}바이트 이하여야 합니다.")
    if not content.startswith(b"%PDF"):
        raise JobValidationError("유효한 PDF 파일이 아닙니다.")


def validate_job_inputs(
    buyer_name: str,
    buyer_phone: str,
    pdf_password: str,
    watermark_start_page: int,
) -> None:
    if not buyer_name.strip():
        raise JobValidationError("구매자 이름을 입력해주세요.")
    if not buyer_phone.strip():
        raise JobValidationError("연락처를 입력해주세요.")
    if not pdf_password.strip():
        raise JobValidationError("PDF 비밀번호를 입력해주세요.")
    try:
        validate_pdf_password(pdf_password)
    except PdfPasswordValidationError as exc:
        raise JobValidationError(str(exc)) from exc
    if watermark_start_page < 1:
        raise JobValidationError("워터마크 시작 페이지는 1 이상이어야 합니다.")


def build_watermark_text(buyer_name: str, buyer_phone: str) -> str:
    return f"이 책은 {buyer_name.strip()} ({buyer_phone.strip()}) 님이 구매하신 전자책입니다."


def build_output_filename(original_filename: str, buyer_name: str) -> str:
    stem = Path(original_filename).stem or "document"
    safe_name = buyer_name.strip().replace("/", "_").replace("\\", "_")
    return f"{stem}_{safe_name}.pdf"


class JobService:
    def __init__(self, store: JobStore, settings: Settings) -> None:
        self._store = store
        self._settings = settings

    def create_job(
        self,
        *,
        file_content: bytes,
        original_filename: str,
        buyer_name: str,
        buyer_phone: str,
        pdf_password: str,
        watermark_start_page: int,
        user_id: str | None,
    ) -> Job:
        validate_pdf_upload(file_content, self._settings.max_upload_bytes)
        validate_job_inputs(
            buyer_name, buyer_phone, pdf_password, watermark_start_page
        )

        job_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        work_dir = ensure_temp_root(self._settings.temp_root) / job_id
        work_dir.mkdir(parents=True, exist_ok=True)

        input_path = work_dir / "input.pdf"
        input_path.write_bytes(file_content)

        output_filename = build_output_filename(original_filename, buyer_name)
        output_path = work_dir / output_filename

        job = Job(
            job_id=job_id,
            status=JobStatus.PENDING,
            progress=0,
            message="대기 중",
            output_filename=output_filename,
            error=None,
            created_at=now,
            expires_at=now + timedelta(seconds=self._settings.job_retention_seconds),
            user_id=user_id,
            work_dir=work_dir,
            input_path=input_path,
            output_path=output_path,
            buyer_name=buyer_name.strip(),
            buyer_phone=buyer_phone.strip(),
        )
        self._store.add(job)
        return job

    def get_job(self, job_id: str) -> Job | None:
        job = self._store.get(job_id)
        if job and job.is_expired:
            remove_job_files(job)
            self._store.remove(job_id)
            return None
        return job

    def process_job(
        self,
        job_id: str,
        pdf_password: str,
        watermark_start_page: int,
    ) -> None:
        job = self._store.get(job_id)
        if job is None:
            return

        self._store.update(
            job_id,
            status=JobStatus.PROCESSING,
            message="처리 시작...",
            progress=0,
        )

        def progress_callback(current: int, total: int, message: str) -> None:
            progress = int((current / total) * 100) if total else 0
            self._store.update(
                job_id,
                progress=progress,
                message=message,
            )

        try:
            watermark_text = build_watermark_text(job.buyer_name, job.buyer_phone)
            add_watermark(
                job.input_path,
                job.output_path,
                watermark_text,
                password=pdf_password,
                buyer_name=job.buyer_name,
                buyer_phone=job.buyer_phone,
                watermark_start_page=watermark_start_page,
                progress_callback=progress_callback,
            )
            self._store.update(
                job_id,
                status=JobStatus.DONE,
                progress=100,
                message="완료!",
                error=None,
            )
        except Exception as exc:
            self._store.update(
                job_id,
                status=JobStatus.FAILED,
                message="처리 실패",
                error=str(exc),
            )

    def delete_job(self, job_id: str) -> bool:
        job = self._store.remove(job_id)
        if job is None:
            return False
        remove_job_files(job)
        return True
