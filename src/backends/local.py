"""Cached, offline Hugging Face image-text-to-text inference."""

from __future__ import annotations

from io import BytesIO
import os
from pathlib import Path


class LocalVLM:
    name = "local-vlm"

    def __init__(self, model_path: str):
        path = Path(model_path).expanduser().resolve()
        if not path.is_dir() or not (path / "config.json").is_file():
            raise ValueError("model_path must be an existing local model directory")
        try:
            import torch
            from transformers import pipeline
        except ImportError as exc:
            raise RuntimeError("Install the local-vlm extra to use model inference") from exc
        if os.environ.get("LOCAL_VLM_THREADS"):
            torch.set_num_threads(int(os.environ["LOCAL_VLM_THREADS"]))
        # A local directory plus offline loading prevents an API call from
        # downloading arbitrary weights at request time.
        self.model_path = str(path)
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        self._pipeline = pipeline("image-text-to-text", model=self.model_path,
                                  trust_remote_code=False,
                                  device=os.environ.get("LOCAL_VLM_DEVICE", "cpu"))

    def infer(self, image_bytes: bytes, prompt: str) -> dict:
        try:
            from PIL import Image, ImageOps
        except ImportError as exc:
            raise RuntimeError("Pillow is required for local VLM inference") from exc
        with Image.open(BytesIO(image_bytes)) as image:
            rgb = ImageOps.exif_transpose(image).convert("RGB")
            rgb.thumbnail((512, 512))
            messages = [{"role": "user", "content": [{"type": "image", "image": rgb}, {"type": "text", "text": prompt}]}]
            output = self._pipeline(text=messages, generate_kwargs={"max_new_tokens": 24, "do_sample": False},
                                    return_full_text=False)
        answer = output[0]["generated_text"]
        if isinstance(answer, list):
            answer = " ".join(str(item.get("text", "")) for item in answer)
        return {"answer": str(answer).strip(), "backend": self.name,
                "model": Path(self.model_path).name, "grounding": "model_generated_unverified", "prompt": prompt}
