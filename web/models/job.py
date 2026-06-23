"""작업 상태 모델."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


@dataclass
class Job:
    job_id: str
    status: JobStatus
    progress: int
    message: str
    output_filename: str | None
    error: str | None
    created_at: datetime
    expires_at: datetime
    user_id: str | None
    work_dir: Path
    input_path: Path
    output_path: Path | None = None
    buyer_name: str = ""
    buyer_phone: str = ""

    def to_api_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "progress": self.progress,
            "message": self.message,
            "output_filename": self.output_filename,
            "error": self.error,
        }

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at
