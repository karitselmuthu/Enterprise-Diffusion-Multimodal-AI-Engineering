"""Determine how many masked positions to commit at each reverse step."""

from __future__ import annotations

import math


def positions_this_step(remaining: int, steps_left: int) -> int:
    if remaining < 0 or steps_left < 1:
        raise ValueError("remaining must be nonnegative and steps_left positive")
    return math.ceil(remaining / steps_left)
