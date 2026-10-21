"""Continuous Gaussian forward process and its closed-form marginal."""

from __future__ import annotations

import math
import random


def linear_beta_schedule(steps: int, start: float = 0.0001, end: float = 0.02) -> list[float]:
    if steps < 1 or not 0 < start <= end < 1:
        raise ValueError("steps must be positive and 0 < start <= end < 1")
    if steps == 1:
        return [start]
    return [start + (end - start) * i / (steps - 1) for i in range(steps)]


def alpha_bars(betas: list[float]) -> list[float]:
    product = 1.0
    result = []
    for beta in betas:
        if not 0 < beta < 1:
            raise ValueError("each beta must lie in (0, 1)")
        product *= 1 - beta
        result.append(product)
    return result


def sample_xt(x0: list[float], alpha_bar: float, rng: random.Random) -> list[float]:
    """Draw q(x_t|x_0) = N(sqrt(alpha_bar)x_0, (1-alpha_bar)I)."""
    if not 0 <= alpha_bar <= 1:
        raise ValueError("alpha_bar must lie in [0, 1]")
    signal, noise = math.sqrt(alpha_bar), math.sqrt(1 - alpha_bar)
    return [signal * value + noise * rng.gauss(0, 1) for value in x0]


def sample_chain(x0: list[float], betas: list[float], rng: random.Random) -> list[list[float]]:
    """Draw q(x_t|x_(t-1)) sequentially, including x_0 in the output."""
    states = [list(x0)]
    for beta in betas:
        signal, noise = math.sqrt(1 - beta), math.sqrt(beta)
        states.append([signal * value + noise * rng.gauss(0, 1) for value in states[-1]])
    return states
