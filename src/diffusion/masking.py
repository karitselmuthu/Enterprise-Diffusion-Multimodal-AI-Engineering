"""Absorbing-mask discrete diffusion and reconstruction helpers."""

from __future__ import annotations

import random

MASK = "[MASK]"


def mask_probability(step: int, total_steps: int) -> float:
    if total_steps < 1 or not 0 <= step <= total_steps:
        raise ValueError("require total_steps >= 1 and 0 <= step <= total_steps")
    return step / total_steps


def mask_tokens(tokens: list[str], probability: float, rng: random.Random, *, ensure_one: bool = False) -> tuple[list[str], list[int]]:
    if not 0 <= probability <= 1:
        raise ValueError("probability must lie in [0, 1]")
    masked = list(tokens)
    eligible = [i for i, token in enumerate(tokens) if token != MASK]
    positions = [i for i in eligible if rng.random() < probability]
    if ensure_one and not positions and eligible:
        positions = [rng.choice(eligible)]
    for i in positions:
        masked[i] = MASK
    return masked, positions


def reconstruct(masked: list[str], predictions: dict[int, str]) -> list[str]:
    result = list(masked)
    for position, token in predictions.items():
        if not 0 <= position < len(result) or result[position] != MASK or token == MASK:
            raise ValueError("predictions must replace masked positions with real tokens")
        result[position] = token
    return result
