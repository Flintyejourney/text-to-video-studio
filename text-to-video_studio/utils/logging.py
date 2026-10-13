"""Rich-backed logger. One call, consistent prefix, no global state."""

from __future__ import annotations

from rich.console import Console
from rich.logging import RichHandler
import logging

_console = Console(stderr=True)
_configured = False


def _configure() -> None:
    global _configured
    if _configured:
        return
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="%H:%M:%S",
        handlers=[RichHandler(console=_console, show_path=False, markup=False)],
    )
    _configured = True


def get_logger(name: str) -> logging.Logger:
    _configure()
    return logging.getLogger(name)