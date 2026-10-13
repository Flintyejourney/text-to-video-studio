"""TOML config loader. Wraps tomllib with a friendly error path."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any


def load_toml(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"config not found: {p}")
    with p.open("rb") as fh:
        return tomllib.load(fh)