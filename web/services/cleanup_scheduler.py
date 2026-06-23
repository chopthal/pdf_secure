"""만료 작업 주기적 정리."""

import asyncio
import logging

from web.services.cleanup import cleanup_expired_jobs
from web.services.job_store import JobStore

logger = logging.getLogger(__name__)


async def run_cleanup_loop(store: JobStore, interval_seconds: int) -> None:
    """interval_seconds마다 만료된 job·임시 파일을 삭제."""
    if interval_seconds <= 0:
        return
    while True:
        await asyncio.sleep(interval_seconds)
        removed = cleanup_expired_jobs(store)
        if removed:
            logger.info("만료 job %d건 정리: %s", len(removed), removed)


def start_cleanup_task(store: JobStore, interval_seconds: int) -> asyncio.Task | None:
    if interval_seconds <= 0:
        return None
    return asyncio.create_task(run_cleanup_loop(store, interval_seconds))
