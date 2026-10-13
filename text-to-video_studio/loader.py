"""Plugin discovery + validation.

Discovery order:
  1. ``config/plugins.toml`` seed entries (explicit)
  2. filesystem scan of ``host.plugin_paths`` for ``plugin.py`` modules

Each candidate is imported in a guarded block; a plugin that fails contract
validation is written to ``runs/_quarantine`` and skipped, never fatal.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import time
from pathlib import Path
from typing import Any

from text_to_video_studio.contracts import CONTRACT_TYPES, Plugin
from text_to_video_studio.utils.logging import get_logger


class PluginLoader:
    def __init__(self, registry: Any, default_cfg: dict, plugin_cfg: dict) -> None:
        self._registry = registry
        self._default = default_cfg
        self._seeds = plugin_cfg.get("plugin", [])
        self._log = get_logger("ttv.loader")

    def discover_and_load(self) -> list[Plugin]:
        loaded: list[Plugin] = []
        seen: set[str] = set()

        for seed in self._seeds:
            if not seed.get("enabled", True):
                self._log.info("skip disabled plugin %s", seed.get("id"))
                continue
            plugin = self._load_module(seed["module"], expect=seed.get("contract"))
            if plugin is None:
                continue
            if plugin.id in seen:
                self._log.warning("duplicate plugin id %s — keeping first", plugin.id)
                continue
            seen.add(plugin.id)
            self._registry.register(plugin)
            loaded.append(plugin)

        for extra in self._scan_filesystem():
            plugin = self._load_module(extra, expect=None)
            if plugin is None or plugin.id in seen:
                continue
            seen.add(plugin.id)
            self._registry.register(plugin)
            loaded.append(plugin)

        return loaded

    def _scan_filesystem(self) -> list[str]:
        modules: list[str] = []
        for root in self._default["host"]["plugin_paths"]:
            base = Path(root)
            if not base.is_dir():
                continue
            for pkg in sorted(base.iterdir()):
                if pkg.is_dir() and (pkg / "plugin.py").is_file():
                    modules.append(f"{root}.{pkg.name}.plugin")
        return modules

    def _load_module(self, dotted: str, expect: str | None) -> Plugin | None:
        try:
            mod = importlib.import_module(dotted)
        except Exception as exc:  # noqa: BLE001 — quarantine, don't crash host
            self._quarantine(dotted, repr(exc))
            return None

        factory = getattr(mod, "PLUGIN", None)
        if factory is None:
            self._quarantine(dotted, "no module-level PLUGIN object")
            return None

        plugin = factory() if callable(factory) else factory
        if not isinstance(plugin, Plugin):
            self._quarantine(dotted, "does not satisfy Plugin protocol")
            return None
        if expect and plugin.contract != expect:
            self._quarantine(dotted, f"contract mismatch: want {expect} got {plugin.contract}")
            return None
        if plugin.contract not in CONTRACT_TYPES:
            self._quarantine(dotted, f"unknown contract {plugin.contract}")
            return None

        self._log.debug("loaded %s (%s v%s)", plugin.id, plugin.contract, plugin.version)
        return plugin

    def _quarantine(self, dotted: str, reason: str) -> None:
        self._log.warning("quarantined %s: %s", dotted, reason)
        qdir = Path(self._default["host"]["quarantine_dir"])
        qdir.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%dT%H%M%S")
        (qdir / f"{dotted.replace('.', '_')}.{stamp}.json").write_text(
            json.dumps({"module": dotted, "reason": reason, "ts": stamp}, indent=2)
        )