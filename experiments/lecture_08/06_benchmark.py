"""Run and persist the diffusion versus autoregressive comparison."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
from src.evaluation.runner import benchmark
from src.evaluation.reports import write_report

report = benchmark()
path = write_report(report, Path(__file__).resolve().parents[2] / "reports" / "lecture_08.json")
print(json.dumps({"report": str(path), **report}, indent=2))
