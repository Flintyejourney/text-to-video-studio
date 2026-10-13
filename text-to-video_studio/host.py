"""Core host: owns the registry, the loader, the queue, and the dispatch loop.

The host is deliberately thin. It knows how to find plugins, validate them
against contracts, and route commands. It does *not* know what a diffusion
backend is — that lives in plugins.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from text_to_video_studio.contracts import CONTRACT_TYPES, Plugin
from text_to_video_studio.loader import PluginLoader
from text_to_video_studio.plugins.registry import PluginRegistry
from text_to_video_studio.services.queue import RenderQueue
from text_to_video_studio.utils.config import load_toml
from text_to_video_studio.utils.logging import get_logger


class Host:
    def __init__(
        self,
        registry: PluginRegistry,
        loader: PluginLoader,
        queue: RenderQueue,
        version: str,
    ) -> None:
        self._registry = registry
        self._loader = loader
        self._queue = queue
        self.version = version

    @classmethod
    def from_config_dir(cls, config_dir: str | Path) -> "Host":
        cfg_dir = Path(config_dir)
        default = load_toml(cfg_dir / "default.toml")
        plugins = load_toml(cfg_dir / "plugins.toml")

        registry = PluginRegistry()
        loader = PluginLoader(registry, default, plugins)
        queue = RenderQueue(max_concurrent=int(default["queue"]["max_concurrent"]))
        return cls(registry, loader, queue, version=str(default["host"]["version"]))

    def boot(self) -> list[Plugin]:
        loaded = self._loader.discover_and_load()
        self._registry.freeze()
        return loaded

    def dispatch(self, argv: Sequence[str]) -> int:
        log = get_logger("ttv.dispatch")
        cmd, *rest = argv
        if cmd == "render":
            prompt = " ".join(rest) or "an empty stage, dust in the light"
            job_id = self._queue.submit(prompt, self._registry)
            log.info("queued job %s: %r", job_id, prompt)
            return 0
        if cmd == "plugins":
            for plugin in self._registry.all():
                log.info("%-24s %-16s v%s", plugin.id, plugin.contract, plugin.version)
            return 0
        log.error("unknown command: %s", cmd)
        return 1