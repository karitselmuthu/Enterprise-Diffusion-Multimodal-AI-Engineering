"""Run four labeled visual probes against a downloaded local VLM."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import argparse
import json
from src.evaluation.multimodal import evaluate_visual_model
from src.evaluation.reports import write_report

parser = argparse.ArgumentParser()
parser.add_argument("--model-path", required=True)
args = parser.parse_args()
report = evaluate_visual_model(args.model_path)
path = write_report(report, Path(__file__).resolve().parents[2] / "reports/lecture_09_vlm.json")
print(json.dumps({"report": str(path), **report}, indent=2))
