"""만료 작업·임시 파일 정리."""

import shutil
from datetime import datetime, timezone
from pathlib import Path

from web.models.job import Job
from web.services.job_store import JobStore


def remove_job_files(job: Job) -> None:
    if job.work_dir.exists():
        shutil.rmtree(job.work_dir, ignore_errors=True)


def cleanup_expired_jobs(store: JobStore, now: datetime | None = None) -> list[str]:
    """만료된 작업을 제거하고 삭제된 job_id 목록을 반환."""
    expired = store.list_expired(now)
    removed_ids: list[str] = []
    for job in expired:
        remove_job_files(job)
        if store.remove(job.job_id):
            removed_ids.append(job.job_id)
    return removed_ids


def ensure_temp_root(temp_root: Path) -> Path:
    temp_root.mkdir(parents=True, exist_ok=True)
    return temp_root
