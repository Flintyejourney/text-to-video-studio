"""Frame-path helpers — deterministic naming so exporters can glob reliably."""

from __future__ import annotations

from pathlib import Path


def frame_name(index: int, width: int = 6) -> str:
    return f"frame_{index:0{width}d}.png"


def frame_paths(work_dir: str | Path, count: int) -> list[Path]:
    base = Path(work_dir)
    return [base / frame_name(i) for i in range(count)]


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p