"""Assess the six declared acceptance criteria from reproducible lab evidence."""

from __future__ import annotations

import json
import math
from pathlib import Path
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def read(name: str) -> dict:
    return json.loads((ROOT / "reports" / name).read_text())


def assess() -> dict:
    cases = read("lecture_09.json")["scenarios"]
    temporal = [row for row in cases if row["category"].startswith("temporal_") or row["category"] in {"historical", "resolved"}]
    temporal_accuracy = sum(row["severity_correct"] for row in temporal) / len(temporal)
    critical_errors = [row["scenario"] for row in temporal if row["severity_expected"] != "high" and row["severity_actual"] == "high"]
    sweep = read("lecture_08_sweep.json")
    sweep_recomputed = runpy.run_path(str(ROOT / "experiments/lecture_08/07_masked_baseline_sweep.py"))["run"]()
    sweep_reproducible = len(sweep["rows"]) == len(sweep_recomputed["rows"]) and all(
        all(math.isclose(saved[key], fresh[key], abs_tol=1e-12, rel_tol=0)
            if isinstance(saved[key], float) else saved[key] == fresh[key]
            for key in saved)
        for saved, fresh in zip(sweep["rows"], sweep_recomputed["rows"])
    )
    security = subprocess.run([sys.executable, "-m", "pytest", "-q",
                               "tests/integration/test_api.py", "tests/unit/test_review.py"], cwd=ROOT,
                              capture_output=True, text=True)
    reliability = read("reliability_lab.json")
    statuses = [row["status"] for row in reliability["repeated"] + reliability["concurrent"]]
    reliability_pass = (all(status == 200 for status in statuses)
                        and reliability["larger"]["status"] == 200
                        and reliability["oversized"]["status"] == 422
                        and reliability["malformed"]["status"] == 422
                        and reliability["client_timeout_observed"]
                        and reliability["recovery"]["status"] == 200
                        and sorted(reliability["simultaneous_review_decisions"]) == [200, 409, 409, 409]
                        and reliability["final_review_status"] == "approved")
    visual = read("lecture_09_dashboard_matrix.json")
    completed = visual["completed"]
    field_accuracy = (sum(row["status_exact"] + row["reading_exact"] for row in visual["rows"]) / (2 * completed)) if completed else None
    visual_status = "pending" if completed < 20 else "pass" if field_accuracy >= 0.9 else "fail"
    return {
        "temporal_reasoning": {"status": "pass" if temporal_accuracy >= 0.95 and not critical_errors else "fail",
                               "accuracy": temporal_accuracy, "case_count": len(temporal), "critical_errors": critical_errors,
                               "scope": "manually curated synthetic temporal scenarios"},
        "vlm_extraction": {"status": visual_status, "completed": completed, "target_minimum": 20,
                           "exact_field_accuracy": field_accuracy, "target_accuracy": 0.9,
                           "both_fields_exact_accuracy": visual.get("both_accuracy"),
                           "scope": "synthetic dashboard status and reading fields"},
        "diffusion_experiment": {"status": "pass" if sweep_reproducible and len(sweep["rows"]) == 36 else "fail",
                                 "settings": len(sweep["rows"]), "reproduced_within_1e_12": sweep_reproducible,
                                 "denoiser_mean_accuracy": sum(row["denoiser_accuracy"] for row in sweep["rows"]) / len(sweep["rows"]),
                                 "baseline_mean_accuracy": sum(row["position_baseline_accuracy"] for row in sweep["rows"]) / len(sweep["rows"])},
        "api_security": {"status": "pass" if security.returncode == 0 else "fail",
                         "test_command": "python -m pytest -q tests/integration/test_api.py tests/unit/test_review.py",
                         "test_output": security.stdout.strip()[-300:]},
        "evidence_validation": {"status": "pending", "automated_unsupported_claim_count": read("lecture_09.json")["summary"]["unsupported_claim_count"],
                                "reason": "Two independent reviewers have not yet judged each generated conclusion against its source."},
        "reliability": {"status": "pass" if reliability_pass else "fail", "repeated_requests": len(reliability["repeated"]),
                        "concurrent_requests": len(reliability["concurrent"]),
                        "review_decision_statuses": reliability["simultaneous_review_decisions"],
                        "final_review_status": reliability["final_review_status"],
                        "scope": "defined mock API workload; local VLM concurrency and server-side cancellation untested"},
    }


if __name__ == "__main__":
    result = assess()
    target = ROOT / "reports/acceptance.json"
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({name: value["status"] for name, value in result.items()}, indent=2))
