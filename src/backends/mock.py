"""Deterministic feature-based substitute for offline architecture exercises."""

from __future__ import annotations

from src.multimodal.image_processor import RGBImage, summarize_image


class MockVLM:
    name = "mock-color-features"

    def infer(self, image: RGBImage, prompt: str) -> dict:
        summary = summarize_image(image)
        return {"answer": f"Image is {summary['width']} by {summary['height']} pixels; mean RGB is {summary['mean_rgb']}; largest mean channel is {summary['dominant_channel']}.", "backend": self.name, "grounding": "pixel_statistics_only", "prompt": prompt}
