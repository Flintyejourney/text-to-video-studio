"""Motion scheduler — turns a seed + prompt into a frame budget.

Kept backend-agnostic: it returns *counts and timings*, not latents. Backends
consume the schedule and do the heavy lifting.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MotionSchedule:
    frames: int
    keyframes: list[int]
    tween_budget: int
    hold_frames: int


def build_schedule(frames: int, fps: int, motion_bias: float = 0.5) -> MotionSchedule:
    motion_bias = max(0.0, min(1.0, motion_bias))
    keyframe_count = max(2, int(frames * (0.15 + 0.25 * (1.0 - motion_bias))))
    stride = max(1, frames // keyframe_count)
    keyframes = list(range(0, frames, stride))
    if keyframes[-1] != frames - 1:
        keyframes.append(frames - 1)
    tween_budget = max(0, frames - len(keyframes))
    hold = 2 if fps <= 24 else 3
    return MotionSchedule(frames=frames, keyframes=keyframes, tween_budget=tween_budget, hold_frames=hold)