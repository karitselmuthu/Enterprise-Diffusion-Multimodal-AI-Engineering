"""Transparent quality, latency and memory measures."""

from __future__ import annotations

import math
import time
import tracemalloc
from collections.abc import Callable


def accuracy(expected: list[str], actual: list[str]) -> float:
    if len(expected) != len(actual) or not expected:
        raise ValueError("equal nonempty sequences are required")
    return sum(left == right for left, right in zip(expected, actual)) / len(expected)


def cross_entropy(target_probabilities: list[float]) -> float:
    if not target_probabilities or any(not 0 < value <= 1 for value in target_probabilities):
        raise ValueError("probabilities must be nonempty and lie in (0, 1]")
    return -sum(math.log(value) for value in target_probabilities) / len(target_probabilities)


def profile(operation: Callable[[], object]) -> dict:
    tracemalloc.start()
    start = time.perf_counter()
    try:
        result = operation()
        elapsed = (time.perf_counter() - start) * 1000
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return {"result": result, "latency_ms": elapsed, "peak_traced_bytes": peak}
