"""Probe a running local API with changing controlled incident inputs."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
from urllib.request import Request, urlopen


def post(url: str, payload: dict) -> dict:
    request = Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=10) as response:
        return json.load(response)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    image = (Path(__file__).resolve().parents[1] / "data/samples/red_alert.ppm").read_bytes()
    encoded = base64.b64encode(image).decode()
    for text in ("Routine check", "Pressure alarm", "Smoke at pump"):
        result = post(args.base_url + "/multimodal/analyze", {"text": text, "image_base64": encoded})
        print(json.dumps({"input": text, "severity": result["severity"], "findings": result["findings"]}))


if __name__ == "__main__":
    main()
