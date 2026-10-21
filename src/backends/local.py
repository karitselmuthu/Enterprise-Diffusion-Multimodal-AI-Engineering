"""Optional local Hugging Face image-text-to-text model inference."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path


class LocalVLM:
    name = "local-vlm"

    def __init__(self, model_path: str):
        if not Path(model_path).is_dir():
            raise ValueError("model_path must be an existing local model directory")
        try:
            from transformers import pipeline
        except ImportError as exc:
            raise RuntimeError("Install the local-vlm extra to use model inference") from exc
        self._pipeline = pipeline("image-text-to-text", model=model_path, model_kwargs={"local_files_only": True, "trust_remote_code": False})

    def infer(self, image_bytes: bytes, prompt: str) -> dict:
        try:
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("Pillow is required for local VLM inference") from exc
        with Image.open(BytesIO(image_bytes)) as image:
            messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": prompt}]}]
            output = self._pipeline(text=messages, images=[image.convert("RGB")], max_new_tokens=128, return_full_text=False)
        answer = output[0]["generated_text"]
        if isinstance(answer, list):
            answer = " ".join(str(item.get("text", "")) for item in answer)
        return {"answer": str(answer), "backend": self.name, "grounding": "model_generated", "prompt": prompt}
