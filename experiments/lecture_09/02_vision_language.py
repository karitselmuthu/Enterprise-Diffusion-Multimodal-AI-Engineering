"""Run mock VLM by default; pass --model-path for a cached local VLM."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import argparse
import json
from src.multimodal.incident_analyzer import analyze_incident

parser = argparse.ArgumentParser()
parser.add_argument("--model-path", default=None)
args = parser.parse_args()
image = (Path(__file__).resolve().parents[2] / "data/samples/red_alert.ppm").read_bytes()
print(json.dumps(analyze_incident(text="Red dashboard alarm", image_bytes=image,
                                  backend="local" if args.model_path else "mock", model_path=args.model_path), indent=2))
