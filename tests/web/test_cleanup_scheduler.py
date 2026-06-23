"""만료 job 주기 정리."""

import asyncio

import pytest

from web.services.cleanup_scheduler import run_cleanup_loop
from web.services.job_store import JobStore


@pytest.mark.asyncio
async def test_cleanup_loop_runs(monkeypatch):
    store = JobStore()
    calls: list[int] = []

    def fake_cleanup(job_store):
        calls.append(1)
        return []

    monkeypatch.setattr(
        "web.services.cleanup_scheduler.cleanup_expired_jobs", fake_cleanup
    )

    task = asyncio.create_task(run_cleanup_loop(store, interval_seconds=0.05))
    await asyncio.sleep(0.15)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert len(calls) >= 1
