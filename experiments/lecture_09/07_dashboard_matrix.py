"""Exact field extraction probe for the cached local VLM."""

from __future__ import annotations

import argparse
import json
import os
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


def run(model_path: str, max_cases: int | None = None) -> dict:
    model = LocalVLM(model_path)
    cases = [json.loads(line) for line in (DATA / "manifest.jsonl").read_text().splitlines()]
    if max_cases is not None:
        if not 1 <= max_cases <= len(cases):
            raise ValueError("max_cases must be within the dashboard manifest")
        cases = cases[:max_cases]
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
        target.write_text(json.dumps(summarize(rows, len(cases), model_path), indent=2) + "\n")
    return summarize(rows, len(cases), model_path)


def summarize(rows: list[dict], target: int, model_path: str | None = None) -> dict:
    count = len(rows)
    metadata_path = Path(model_path) / "download_metadata.json" if model_path else None
    metadata = json.loads(metadata_path.read_text()) if metadata_path and metadata_path.exists() else {}
    by_variant = {}
    for variant in sorted({row["variant"] for row in rows}):
        group = [row for row in rows if row["variant"] == variant]
        by_variant[str(variant)] = {"count": len(group),
                                    "status_accuracy": sum(row["status_exact"] for row in group) / len(group),
                                    "reading_accuracy": sum(row["reading_exact"] for row in group) / len(group),
                                    "both_accuracy": sum(row["both_exact"] for row in group) / len(group)}
    latencies = sorted(row["latency_ms"] for row in rows)
    return {"completed": count, "target": target,
            "model_id": metadata.get("model_id"), "revision": metadata.get("revision"),
            "prompt": "Read this dashboard. Return the exact status text and exact numeric reading with units. If unreadable, say unreadable.",
            "local_vlm_threads": int(os.environ.get("LOCAL_VLM_THREADS", "4")), "image_max_side_pixels": 512,
            "matching_rule": "Case- and punctuation-normalized complete field value must appear contiguously in the free-form answer; extra text is allowed.",
            "status_accuracy": sum(row["status_exact"] for row in rows) / count if count else None,
            "reading_accuracy": sum(row["reading_exact"] for row in rows) / count if count else None,
            "both_accuracy": sum(row["both_exact"] for row in rows) / count if count else None,
            "mean_latency_ms": sum(row["latency_ms"] for row in rows) / count if count else None,
            "p95_latency_ms": latencies[max(0, (95 * count + 99) // 100 - 1)] if count else None,
            "by_variant": by_variant,
            "rows": rows,
            "ground_truth_origin": "programmatically rendered synthetic labels; no independent human validation"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", default="data/models/smolvlm-256m-instruct")
    parser.add_argument("--summarize-only", action="store_true")
    parser.add_argument("--max-cases", type=int, default=None)
    args = parser.parse_args()
    if args.summarize_only:
        target = ROOT / "reports" / "lecture_09_dashboard_matrix.json"
        rows = json.loads(target.read_text())["rows"]
        report = summarize(rows, args.max_cases or len((DATA / "manifest.jsonl").read_text().splitlines()), args.model_path)
        target.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: value for key, value in report.items() if key != "rows"}, indent=2))
    else:
        print(json.dumps(run(args.model_path, args.max_cases), indent=2))
