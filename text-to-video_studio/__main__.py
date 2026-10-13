"""Entry point for the ``ttv`` console script and ``python -m`` invocation."""

from __future__ import annotations

import sys

from text_to_video_studio.host import Host
from text_to_video_studio.utils.logging import get_logger


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    log = get_logger("ttv.main")

    host = Host.from_config_dir("config")
    loaded = host.boot()

    if not loaded:
        log.error("no plugins loaded — check config/plugins.toml and plugins/")
        return 2

    log.info("booted text-to-video-studio v%s with %d plugins", host.version, len(loaded))

    if not argv:
        log.info("no command given; try: ttv render \"a fox on a rooftop at dusk\"")
        return 0

    return host.dispatch(argv)


if __name__ == "__main__":
    raise SystemExit(main())