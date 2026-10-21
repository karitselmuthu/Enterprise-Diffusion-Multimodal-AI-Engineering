"""Save structured benchmark reports."""

from __future__ import annotations

import json
from pathlib import Path


def write_report(data: dict, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return target
