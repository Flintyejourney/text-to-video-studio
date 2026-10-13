"""CLI handler — parses `ttv render|plugins|inspect` into host calls."""

from __future__ import annotations

import argparse
import asyncio

from text_to_video_studio.host import Host
from text_to_video_studio.models.shot import Shot
from text_to_video_studio.services.scheduler import build_schedule


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("ttv", description="text-to-video studio")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("render", help="render a prompt to video")
    r.add_argument("prompt", nargs="+")
    r.add_argument("--width", type=int, default=832)
    r.add_argument("--height", type=int, default=480)
    r.add_argument("--frames", type=int, default=48)
    r.add_argument("--fps", type=int, default=24)
    r.add_argument("--seed", type=int, default=6767)
    r.add_argument("--motion", type=float, default=0.5)

    sub.add_parser("plugins", help="list loaded plugins")
    return p


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    host = Host.from_config_dir("config")
    host.boot()

    if args.cmd == "plugins":
        return host.dispatch(["plugins"])

    shot = Shot(
        prompt=" ".join(args.prompt),
        width=args.width, height=args.height,
        frames=args.frames, fps=args.fps,
        seed=args.seed, motion_bias=args.motion,
    )
    schedule = build_schedule(shot.frames, shot.fps, shot.motion_bias)
    asyncio.run(_render(host, shot, schedule))
    return 0


async def _render(host: Host, shot: Shot, schedule) -> None:  # pragma: no cover
    host.dispatch(["render", shot.prompt])