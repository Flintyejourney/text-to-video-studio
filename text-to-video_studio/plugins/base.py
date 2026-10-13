"""Convenience base classes so plugin authors don't re-implement boilerplate."""

from __future__ import annotations

from text_to_video_studio.contracts import PluginContext, PluginResult


class BackendBase:
    contract = "BackendPlugin"

    async def run(self, ctx: PluginContext) -> PluginResult:  # pragma: no cover - abstract
        raise NotImplementedError


class MotionBase:
    contract = "MotionPlugin"

    async def run(self, ctx: PluginContext) -> PluginResult:  # pragma: no cover
        raise NotImplementedError


class UpscaleBase:
    contract = "UpscalePlugin"

    async def run(self, ctx: PluginContext) -> PluginResult:  # pragma: no cover
        raise NotImplementedError


class CaptionBase:
    contract = "CaptionPlugin"

    async def run(self, ctx: PluginContext) -> PluginResult:  # pragma: no cover
        raise NotImplementedError


class ExportBase:
    contract = "ExportPlugin"

    async def run(self, ctx: PluginContext) -> PluginResult:  # pragma: no cover
        raise NotImplementedError