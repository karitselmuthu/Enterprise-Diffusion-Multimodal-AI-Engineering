"""Curated incident scenarios and optional real-VLM visual evaluation."""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
import sys
import time

from src.multimodal.incident_analyzer import analyze_incident
from .metrics import profile

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "evaluation"


def scenarios() -> list[dict]:
    return [json.loads(line) for line in (DATA / "incidents.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]


def _asset(name: str | None) -> bytes | None:
    if name is None:
        return None
    path = (DATA / name).resolve()
    if not path.is_relative_to(ROOT / "data"):
        raise ValueError("scenario asset must remain inside data/")
    return path.read_bytes()


def _unsupported_claims(result: dict) -> int:
    evidence = {item["source"]: item for item in result["evidence"]}
    unsupported = 0
    for finding in result["findings"]:
        cited = finding.get("sources", [])
        if not cited or any(source not in evidence for source in cited):
            unsupported += 1
            continue
        if finding["claim"].startswith("Text contains incident terms:"):
            cited_text = " ".join(str(evidence[source]["content"]).lower() for source in cited)
            terms = [term.strip() for term in finding["claim"].split(":", 1)[1].split(",")]
            if any(term not in cited_text for term in terms):
                unsupported += 1
        if finding["claim"].startswith("Unverified model observation:") and finding.get("verification") != "requires_human_review":
            unsupported += 1
    return unsupported


def evaluate_scenarios() -> dict:
    rows = []
    by_category: dict[str, list[bool]] = defaultdict(list)
    for case in scenarios():
        image, document = _asset(case.get("image")), _asset(case.get("document"))
        measured = profile(lambda: analyze_incident(text=case["report"], image_bytes=image,
                                                    document_bytes=document, document_name=case.get("document")))
        result = measured["result"]
        sources = {item["source"] for item in result["evidence"]}
        unsupported = _unsupported_claims(result)
        severity_correct = case["expected_severity"] == result["severity"]
        by_category[case["category"]].append(severity_correct)
        rows.append({"scenario": case["id"], "category": case["category"],
                     "severity_expected": case["expected_severity"], "severity_actual": result["severity"],
                     "severity_correct": severity_correct,
                     "extraction_success": set(case["expected_sources"]) <= sources,
                     "evidence_grounded": unsupported == 0,
                     "unsupported_claims": unsupported,
                     "task_complete": result["severity"] in {"high", "medium", "undetermined"} and bool(sources),
                     "latency_ms": measured["latency_ms"], "peak_traced_bytes": measured["peak_traced_bytes"]})
    failures = []
    for name, arguments in [
        ("corrupt_image", {"text": "check", "image_bytes": b"bad image"}),
        ("missing_document_name", {"text": "check", "document_bytes": b"text"}),
        ("unsupported_document", {"text": "check", "document_bytes": b"text", "document_name": "data.bin"}),
    ]:
        try:
            analyze_incident(**arguments)
            rejected = False
        except ValueError:
            rejected = True
        failures.append({"case": name, "rejected_as_expected": rejected})
    performance_by_size = []
    for side in (2, 20, 100):
        image_data = (f"P3\n{side} {side}\n255\n" + "255 0 0 " * (side * side)).encode()
        measured = profile(lambda: analyze_incident(text="pressure alarm", image_bytes=image_data))
        performance_by_size.append({"image_side_pixels": side, "latency_ms": measured["latency_ms"],
                                    "peak_traced_bytes": measured["peak_traced_bytes"]})
    count = len(rows)
    return {"dataset": {"path": "data/evaluation/incidents.jsonl", "scenario_count": count,
                        "label_origin": "manually curated synthetic examples; no independent human validation"},
            "scenarios": rows, "failure_tests": failures, "performance_by_size": performance_by_size,
            "summary": {
                "severity_accuracy": sum(row["severity_correct"] for row in rows) / count,
                "severity_accuracy_by_category": {category: sum(values) / len(values) for category, values in by_category.items()},
                "extraction_accuracy": sum(row["extraction_success"] for row in rows) / count,
                "evidence_grounding_rate": sum(row["evidence_grounded"] for row in rows) / count,
                "unsupported_claim_count": sum(row["unsupported_claims"] for row in rows),
                "task_completion_rate": sum(row["task_complete"] for row in rows) / count,
                "expected_failure_rejection_rate": sum(row["rejected_as_expected"] for row in failures) / len(failures),
            }}


def evaluate_visual_model(model_path: str) -> dict:
    """Probe visible status text with a cached local model, without promoting its claims."""
    cases = [("smoke_dashboard.png", "smoke"), ("pressure_dashboard.png", "pressure"),
             ("normal_dashboard.png", "normal"), ("network_dashboard.png", "failure")]
    metadata_path = Path(model_path) / "download_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    rows = []
    for filename, expected_word in cases:
        print(f"Evaluating local VLM: {filename}", file=sys.stderr, flush=True)
        start = time.perf_counter()
        result = analyze_incident(text="", image_bytes=(DATA / filename).read_bytes(),
                                  backend="local", model_path=model_path)
        answer = result["vlm"]["answer"]
        rows.append({"image": filename, "expected_visible_word": expected_word,
                     "model_answer": answer, "word_present": expected_word in answer.lower(),
                     "severity": result["severity"], "human_review_required":
                     any(item.get("verification") == "unverified_model_output" for item in result["evidence"]),
                     "latency_ms": (time.perf_counter() - start) * 1000})
    return {"model": result["vlm"].get("model"), "model_id": metadata.get("model_id"),
            "revision": metadata.get("revision"), "cases": rows,
            "visible_word_recall": sum(row["word_present"] for row in rows) / len(rows),
            "note": "Visible-word recall is a narrow synthetic OCR proxy. Generated observations remain unverified."}
