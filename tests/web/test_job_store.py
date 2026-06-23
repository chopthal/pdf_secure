"""Task 2a: job_store 단위 테스트."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from web.models.job import Job, JobStatus
from web.services.job_store import JobStore


def _make_job(job_id: str = "job-1") -> Job:
    now = datetime.now(timezone.utc)
    work = Path(f"/tmp/{job_id}")
    return Job(
        job_id=job_id,
        status=JobStatus.PENDING,
        progress=0,
        message="대기",
        output_filename="out.pdf",
        error=None,
        created_at=now,
        expires_at=now + timedelta(hours=1),
        user_id="user-1",
        work_dir=work,
        input_path=work / "input.pdf",
    )


class TestJobStore:
    def test_add_and_get(self, job_store: JobStore):
        job = _make_job()
        job_store.add(job)
        assert job_store.get("job-1") is job

    def test_update_fields(self, job_store: JobStore):
        job_store.add(_make_job())
        updated = job_store.update("job-1", status=JobStatus.DONE, progress=100)
        assert updated is not None
        assert updated.status == JobStatus.DONE
        assert updated.progress == 100

    def test_list_expired(self, job_store: JobStore):
        job = _make_job()
        job_store.add(job)
        now = job.expires_at + timedelta(seconds=1)
        expired = job_store.list_expired(now)
        assert len(expired) == 1

    def test_remove(self, job_store: JobStore):
        job_store.add(_make_job())
        removed = job_store.remove("job-1")
        assert removed is not None
        assert job_store.get("job-1") is None
