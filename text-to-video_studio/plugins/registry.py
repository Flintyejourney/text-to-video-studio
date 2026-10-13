"""Thread-safe plugin registry. Frozen after boot to prevent hot-swap drift."""

from __future__ import annotations

import threading

from text_to_video_studio.contracts import Plugin


class RegistryFrozenError(RuntimeError):
    pass


class PluginRegistry:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._by_id: dict[str, Plugin] = {}
        self._by_contract: dict[str, list[Plugin]] = {}
        self._frozen = False

    def register(self, plugin: Plugin) -> None:
        with self._lock:
            if self._frozen:
                raise RegistryFrozenError("registry is frozen; restart host to add plugins")
            self._by_id[plugin.id] = plugin
            self._by_contract.setdefault(plugin.contract, []).append(plugin)

    def freeze(self) -> None:
        with self._lock:
            self._frozen = True

    def get(self, plugin_id: str) -> Plugin | None:
        return self._by_id.get(plugin_id)

    def by_contract(self, contract: str) -> list[Plugin]:
        return list(self._by_contract.get(contract, ()))

    def all(self) -> list[Plugin]:
        return list(self._by_id.values())

    def __len__(self) -> int:
        return len(self._by_id)