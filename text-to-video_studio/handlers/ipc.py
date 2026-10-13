"""Line-oriented JSON IPC so non-Python backends (C++/C#/Java) can drive the host.

Protocol: one JSON object per line on stdin, one response per line on stdout.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from text_to_video_studio.host import Host


def serve(host: Host) -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg: dict[str, Any] = json.loads(line)
        except json.JSONDecodeError as exc:
            _reply({"ok": False, "error": f"bad json: {exc}"})
            continue
        _handle(host, msg)
    return 0


def _handle(host: Host, msg: dict[str, Any]) -> None:
    op = msg.get("op")
    if op == "plugins":
        _reply({"ok": True, "plugins": [
            {"id": p.id, "contract": p.contract, "version": p.version} for p in host._registry.all()  # noqa: SLF001
        ]})
    elif op == "render":
        job_id = host._queue.submit(str(msg.get("prompt", "")), host._registry)  # noqa: SLF001
        _reply({"ok": True, "job_id": job_id})
    else:
        _reply({"ok": False, "error": f"unknown op {op!r}"})


def _reply(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()