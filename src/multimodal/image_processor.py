"""Small RGB image loader; Pillow handles common formats, P3 PPM works offline."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO


@dataclass
class RGBImage:
    width: int
    height: int
    pixels: list[tuple[int, int, int]]


def load_image(data: bytes, *, max_pixels: int = 4_000_000) -> RGBImage:
    if len(data) > 5_000_000:
        raise ValueError("image exceeds 5 MB limit")
    if data.lstrip().startswith(b"P3"):
        try:
            lines = [line.split(b"#", 1)[0] for line in data.splitlines()]
            parts = b" ".join(lines).split()
            if parts[0] != b"P3":
                raise ValueError("invalid P3 header")
            width, height, maximum = map(int, parts[1:4])
            if width <= 0 or height <= 0 or width * height > max_pixels or not 0 < maximum <= 65535:
                raise ValueError("invalid image dimensions or color maximum")
            values = [int(value) for value in parts[4:]]
            if len(values) != width * height * 3 or any(not 0 <= value <= maximum for value in values):
                raise ValueError("invalid pixel data")
            pixels = [tuple(round(value * 255 / maximum) for value in values[i:i + 3]) for i in range(0, len(values), 3)]
            return RGBImage(width, height, pixels)
        except (IndexError, TypeError) as exc:
            raise ValueError("invalid P3 PPM image") from exc
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError as exc:
        raise RuntimeError("Pillow is required for PNG and JPEG images") from exc
    try:
        with Image.open(BytesIO(data)) as image:
            if not 0 < image.width * image.height <= max_pixels:
                raise ValueError("invalid or oversized image")
            rgb = image.convert("RGB")
            pixels = rgb.get_flattened_data() if hasattr(rgb, "get_flattened_data") else rgb.getdata()
            return RGBImage(rgb.width, rgb.height, list(pixels))
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("unsupported or corrupt image") from exc


def summarize_image(image: RGBImage) -> dict:
    if not image.pixels:
        raise ValueError("image has no pixels")
    count = len(image.pixels)
    means = [round(sum(pixel[channel] for pixel in image.pixels) / count, 2) for channel in range(3)]
    names = ["red", "green", "blue"]
    dominant = names[max(range(3), key=lambda channel: means[channel])]
    return {"width": image.width, "height": image.height, "mean_rgb": means, "dominant_channel": dominant}
