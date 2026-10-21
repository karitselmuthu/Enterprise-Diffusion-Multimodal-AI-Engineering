"""Backend selection without implicit model downloads."""

from __future__ import annotations

from src.backends.local import LocalVLM
from src.backends.mock import MockVLM


def get_backend(name: str = "mock", *, model_path: str | None = None):
    if name == "mock":
        return MockVLM()
    if name == "local":
        if not model_path:
            raise ValueError("local backend requires model_path")
        return LocalVLM(model_path)
    raise ValueError("backend must be mock or local")
