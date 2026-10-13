"""In-process render queue.

Bounded concurrency via a semaphore. Jobs are pure data; the actual render
is delegated to whichever BackendPlugin is registered. Retries use
exponential backoff with jitter (``retry_attempts`` from config).
"""

from __future__ import annotations

import asyncio
import random
import uuid
from dataclasses import dataclass, field

from text_to_video_studio.contracts import PluginContext, PluginResult
from text_to_video_studio.utils.logging import get_logger


@dataclass(slots=True)
class RenderJob:
    id: str
    prompt: str
    attempts: int = 0
    result: PluginResult | None = None
    meta: dict = field(default_factory=dict)


class RenderQueue:
    def __init__(self, max_concurrent: int = 2, retry_attempts: int = 3) -> None:
        self._sem = asyncio.Semaphore(max_concurrent)
        self._retry = retry_attempts
        self._log = get_logger("ttv.queue")
        self._jobs: dict[str, RenderJob] = {}

    def submit(self, prompt: str, registry) -> str:
        job = RenderJob(id=uuid.uuid4().hex[:12], prompt=prompt)
        self._jobs[job.id] = job
        backends = registry.by_contract("BackendPlugin")
        if not backends:
            job.result = PluginResult(ok=False, error="no BackendPlugin registered")
            return job.id
        asyncio.get_event_loop().create_task(self._run(job, backends[0]))
        return job.id

    async def _run(self, job: RenderJob, backend) -> None:
        ctx = PluginContext(
            prompt=job.prompt,
            width=832, height=480, fps=24, frames=48,
            seed=6767, device="auto", work_dir=f"runs/{job.id}",
        )
        async with self._sem:
            for attempt in range(1, self._retry + 1):
                job.attempts = attempt
                try:
                    job.result = await backend.run(ctx)
                    if job.result.ok:
                        return
                except Exception as exc:  # noqa: BLE001
                    self._log.warning("job %s attempt %d failed: %s", job.id, attempt, exc)
                await asyncio.sleep((2 ** attempt) * 0.1 + random.random() * 0.1)
            job.result = job.result or PluginResult(ok=False, error="exhausted retries")