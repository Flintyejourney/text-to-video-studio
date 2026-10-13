"""Reference BackendPlugin — deterministic noise so the pipeline is testable
without a GPU. Real backends (torch/diffusers, ONNX) follow the same shape.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from text_to_video_studio.contracts import PluginContext, PluginResult
from text_to_video_studio.plugins.base import BackendBase
from text_to_video_studio.utils.frames import ensure_dir, frame_name
from text_to_video_studio.utils.logging import get_logger


class MockDiffusionBackend(BackendBase):
    id = "mock_diffusion"
    version = "0.1.0"

    async def run(self, ctx: PluginContext) -> PluginResult:
        log = get_logger("ttv.backend.mock")
        out = ensure_dir(ctx.work_dir)
        seed = hashlib.sha256(f"{ctx.prompt}:{ctx.seed}".encode()).digest()

        frames: list[str] = []
        for i in range(ctx.frames):
            p = out / frame_name(i)
            p.write_bytes(seed + i.to_bytes(4, "little"))
            frames.append(str(p))

        log.info("mock backend produced %d frames for %r", len(frames), ctx.prompt)
        return PluginResult(ok=True, frames=frames, artifact=str(out), stats={"frames": float(len(frames))})


def PLUGIN() -> MockDiffusionBackend:
    return MockDiffusionBackend()