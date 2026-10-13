"""On-disk cache for backend weights. Never downloads unless enabled."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import httpx

from text_to_video_studio.utils.logging import get_logger


class ModelCache:
    def __init__(self, root: str = "models_cache", mirror: str = "", allow_remote: bool = True) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.mirror = mirror.rstrip("/")
        self.allow_remote = allow_remote
        self._log = get_logger("ttv.cache")

    def path_for(self, name: str) -> Path:
        return self.root / name

    def has(self, name: str) -> bool:
        return self.path_for(name).is_file()

    def fetch(self, name: str) -> Path:
        dest = self.path_for(name)
        if dest.is_file():
            return dest
        if not self.allow_remote or not self.mirror:
            raise FileNotFoundError(f"weight {name!r} not cached and remote disabled")
        url = f"{self.mirror}/{name}"
        self._log.info("fetching %s", url)
        tmp = dest.with_suffix(dest.suffix + ".part")
        with httpx.stream("GET", url, timeout=120.0, follow_redirects=True) as resp:
            resp.raise_for_status()
            with tmp.open("wb") as fh:
                for chunk in resp.iter_bytes(1 << 20):
                    fh.write(chunk)
        os.replace(tmp, dest)
        return dest

    @staticmethod
    def digest(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for block in iter(lambda: fh.read(1 << 20), b""):
                h.update(block)
        return h.hexdigest()