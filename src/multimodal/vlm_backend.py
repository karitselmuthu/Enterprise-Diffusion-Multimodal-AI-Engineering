"""Backend selection without implicit model downloads."""

from __future__ import annotations

from functools import lru_cache
import os
from pathlib import Path

from src.backends.local import LocalVLM
from src.backends.mock import MockVLM


@lru_cache(maxsize=2)
def _local(path: str) -> LocalVLM:
    return LocalVLM(path)


def get_backend(name: str = "mock", *, model_path: str | None = None):
    if name == "mock":
        return MockVLM()
    if name == "local":
        chosen = model_path or os.environ.get("LOCAL_VLM_MODEL_PATH")
        if not chosen:
            raise ValueError("local backend requires a configured LOCAL_VLM_MODEL_PATH")
        return _local(str(Path(chosen).expanduser().resolve()))
    raise ValueError("backend must be mock or local")
