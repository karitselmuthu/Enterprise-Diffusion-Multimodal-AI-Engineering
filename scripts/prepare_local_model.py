"""Download a pinned VLM snapshot outside Git tracking for the optional lab."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", default="HuggingFaceTB/SmolVLM-256M-Instruct")
    parser.add_argument("--revision", default="main")
    parser.add_argument("--output", type=Path, default=Path("data/models/smolvlm-256m-instruct"))
    args = parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        raise SystemExit(f"Output is not empty: {args.output}")
    try:
        from huggingface_hub import HfApi, snapshot_download
    except ImportError as exc:
        raise SystemExit("Install .[local-vlm] first") from exc
    info = HfApi().model_info(args.model_id, revision=args.revision)
    target = args.output.resolve()
    target.mkdir(parents=True, exist_ok=True)
    snapshot_download(repo_id=args.model_id, revision=info.sha, local_dir=target,
                      max_workers=2, ignore_patterns=["onnx/*", "*.onnx", "*.md", "*.png", "*.jpg", "*.jpeg"])
    metadata = {"model_id": args.model_id, "revision": info.sha, "path": str(target)}
    (target / "download_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
