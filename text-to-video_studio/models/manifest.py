"""Render manifest — what a finished job leaves behind on disk."""

from __future__ import annotations

from pydantic import BaseModel

from text_to_video_studio.models.shot import Shot


class PluginRef(BaseModel):
    id: str
    contract: str
    version: str


class RenderManifest(BaseModel):
    job_id: str
    shot: Shot
    plugins: list[PluginRef]
    artifact: str | None = None
    duration_s: float = 0.0
    fps: int = 24
    ok: bool = True
    error: str | None = None

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)