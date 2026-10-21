"""Exact field extraction probe for the cached local VLM."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.backends.local import LocalVLM

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "evaluation" / "dashboard_matrix"


def normalized(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def run(model_path: str) -> dict:
    model = LocalVLM(model_path)
    cases = [json.loads(line) for line in (DATA / "manifest.jsonl").read_text().splitlines()]
    target = ROOT / "reports" / "lecture_09_dashboard_matrix.json"
    existing = json.loads(target.read_text())["rows"] if target.exists() else []
    rows = existing if [row["image"] for row in existing] == [case["image"] for case in cases[:len(existing)]] else []
    for case in cases[len(rows):]:
        print(f"VLM {len(rows) + 1}/{len(cases)}: {case['image']}", file=sys.stderr, flush=True)
        start = time.perf_counter()
        answer = model.infer((DATA / case["image"]).read_bytes(),
                             "Read this dashboard. Return the exact status text and exact numeric reading with units. If unreadable, say unreadable.")["answer"]
        actual = normalized(answer)
        status_exact = normalized(case["status"]) in actual
        reading_exact = normalized(case["reading"]) in actual
        rows.append({**case, "answer": answer, "status_exact": status_exact, "reading_exact": reading_exact,
                     "both_exact": status_exact and reading_exact, "latency_ms": (time.perf_counter() - start) * 1000})
        target.parent.mkdir(exist_ok=True)
        target.write_text(json.dumps(summarize(rows, len(cases)), indent=2) + "\n")
    return summarize(rows, len(cases))


def summarize(rows: list[dict], target: int) -> dict:
    count = len(rows)
    return {"completed": count, "target": target,
            "status_accuracy": sum(row["status_exact"] for row in rows) / count if count else None,
            "reading_accuracy": sum(row["reading_exact"] for row in rows) / count if count else None,
            "both_accuracy": sum(row["both_exact"] for row in rows) / count if count else None,
            "mean_latency_ms": sum(row["latency_ms"] for row in rows) / count if count else None,
            "rows": rows,
            "ground_truth_origin": "programmatically rendered synthetic labels; no independent human validation"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", default="data/models/smolvlm-256m-instruct")
    parser.add_argument("--summarize-only", action="store_true")
    args = parser.parse_args()
    if args.summarize_only:
        target = ROOT / "reports" / "lecture_09_dashboard_matrix.json"
        rows = json.loads(target.read_text())["rows"]
        report = summarize(rows, len((DATA / "manifest.jsonl").read_text().splitlines()))
        target.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: value for key, value in report.items() if key != "rows"}, indent=2))
    else:
        print(json.dumps(run(args.model_path), indent=2))
