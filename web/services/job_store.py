"""인메모리 작업 저장소 (스레드 안전)."""

import threading
from datetime import datetime, timezone

from web.models.job import Job


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def add(self, job: Job) -> None:
        with self._lock:
            self._jobs[job.job_id] = job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def update(self, job_id: str, **fields) -> Job | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            for key, value in fields.items():
                setattr(job, key, value)
            return job

    def list_expired(self, now: datetime | None = None) -> list[Job]:
        current = now or datetime.now(timezone.utc)
        with self._lock:
            return [job for job in self._jobs.values() if current >= job.expires_at]

    def remove(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.pop(job_id, None)

    def clear(self) -> None:
        with self._lock:
            self._jobs.clear()
