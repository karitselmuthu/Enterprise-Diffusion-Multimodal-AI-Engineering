"""Interpretable color-feature encoder and simple text-color projection."""

from __future__ import annotations

import math
import re

from .image_processor import RGBImage

COLORS = {"red": (1.0, 0.0, 0.0), "green": (0.0, 1.0, 0.0), "blue": (0.0, 0.0, 1.0), "yellow": (1.0, 1.0, 0.0), "white": (1.0, 1.0, 1.0), "black": (0.0, 0.0, 0.0)}


def encode_image(image: RGBImage) -> list[float]:
    count = len(image.pixels)
    if not count:
        raise ValueError("image has no pixels")
    return [sum(pixel[channel] for pixel in image.pixels) / (255 * count) for channel in range(3)]


def encode_text(text: str) -> list[float]:
    words = re.findall(r"[a-z]+", text.lower())
    matches = [COLORS[word] for word in words if word in COLORS]
    if not matches:
        return [0.0, 0.0, 0.0]
    return [sum(color[i] for color in matches) / len(matches) for i in range(3)]


def cosine_similarity(first: list[float], second: list[float]) -> float | None:
    if len(first) != len(second) or not first:
        raise ValueError("equal nonempty vectors are required")
    norm_first = math.sqrt(sum(value * value for value in first))
    norm_second = math.sqrt(sum(value * value for value in second))
    if norm_first == 0 or norm_second == 0:
        return None
    return sum(a * b for a, b in zip(first, second)) / (norm_first * norm_second)
