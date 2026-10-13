"""Shot schema — the atomic unit of a text-to-video request."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class Shot(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    width: int = Field(832, ge=64, le=4096)
    height: int = Field(480, ge=64, le=4096)
    frames: int = Field(48, ge=1, le=2048)
    fps: int = Field(24, ge=1, le=120)
    seed: int = Field(6767, ge=0, le=2**31 - 1)
    negative: str = ""
    motion_bias: float = Field(0.5, ge=0.0, le=1.0)

    @field_validator("width", "height")
    @classmethod
    def _multiple_of_8(cls, v: int) -> int:
        if v % 8:
            raise ValueError("dimensions must be multiples of 8 for diffusion backends")
        return v

    def duration_s(self) -> float:
        return self.frames / self.fps