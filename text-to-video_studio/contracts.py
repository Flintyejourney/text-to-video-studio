"""Shared contracts every plugin must satisfy.

A plugin is any object exposing ``id``, ``contract``, ``version``, and the
``run`` coroutine. Contracts are string-tagged so the registry stays
decoupled from concrete classes (C++/C#/Java backends can bridge via an IPC
shim that speaks the same manifest).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Plugin(Protocol):
    id: str
    contract: str
    version: str

    async def run(self, ctx: "PluginContext") -> "PluginResult": ...


@dataclass(slots=True)
class PluginContext:
    prompt: str
    width: int
    height: int
    fps: int
    frames: int
    seed: int
    device: str
    work_dir: str
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PluginResult:
    ok: bool
    frames: list[str] = field(default_factory=list)
    artifact: str | None = None
    error: str | None = None
    stats: dict[str, float] = field(default_factory=dict)


CONTRACT_TYPES: tuple[str, ...] = (
    "BackendPlugin",
    "MotionPlugin",
    "UpscalePlugin",
    "CaptionPlugin",
    "ExportPlugin",
)