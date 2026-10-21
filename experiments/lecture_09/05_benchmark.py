"""Persist scenario quality and performance measurements."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
from src.evaluation.multimodal import evaluate_scenarios
from src.evaluation.reports import write_report

report = evaluate_scenarios()
path = write_report(report, Path(__file__).resolve().parents[2] / "reports/lecture_09.json")
print(json.dumps({"report": str(path), **report}, indent=2))
