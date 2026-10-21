"""Small scenario suite with explicit expected evidence and failure behavior."""

from __future__ import annotations

from pathlib import Path

from src.multimodal.incident_analyzer import analyze_incident
from .metrics import profile

SAMPLES = Path(__file__).resolve().parents[2] / "data" / "samples"


def scenarios() -> list[dict]:
    return [
        {"name": "smoke_report", "text": "Smoke near the motor", "image": "red_alert.ppm", "expected_severity": "high", "expected_source": "report_text"},
        {"name": "pressure_document", "text": "Operator check", "document": "incident_note.txt", "expected_severity": "medium", "expected_source": "document_text"},
        {"name": "green_image_only", "text": "", "image": "green_status.ppm", "expected_severity": "undetermined", "expected_source": "image_pixels"},
        {"name": "routine_report", "text": "Routine inspection complete", "expected_severity": "undetermined", "expected_source": "report_text"},
        {"name": "leak_report", "text": "Leak at east valve", "image": "green_status.ppm", "expected_severity": "medium", "expected_source": "report_text"},
    ]


def evaluate_scenarios() -> dict:
    rows = []
    for case in scenarios():
        image = (SAMPLES / case["image"]).read_bytes() if "image" in case else None
        document = (SAMPLES / case["document"]).read_bytes() if "document" in case else None
        measured = profile(lambda: analyze_incident(text=case["text"], image_bytes=image,
                                                    document_bytes=document, document_name=case.get("document")))
        result = measured["result"]
        sources = {item["source"] for item in result["evidence"]}
        grounded = all(set(finding["sources"]) <= sources for finding in result["findings"])
        unsupported = 0
        for finding in result["findings"]:
            if not set(finding["sources"]) <= sources:
                unsupported += 1
            if "Text contains incident terms:" in finding["claim"]:
                cited_text = " ".join(str(item["content"]).lower() for item in result["evidence"] if item["source"] in finding["sources"])
                cited_terms = [term.strip() for term in finding["claim"].split(":", 1)[1].split(",")]
                if any(term not in cited_text for term in cited_terms):
                    unsupported += 1
        grounded = grounded and unsupported == 0
        rows.append({"scenario": case["name"], "severity_expected": case["expected_severity"],
                     "severity_actual": result["severity"], "extraction_success": case["expected_source"] in sources,
                     "evidence_grounded": grounded, "unsupported_claims": unsupported,
                     "task_complete": bool(result["severity"] and result["evidence"]),
                     "latency_ms": measured["latency_ms"], "peak_traced_bytes": measured["peak_traced_bytes"]})
    count = len(rows)
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
    return {"scenarios": rows, "failure_tests": failures, "performance_by_size": performance_by_size, "summary": {
        "severity_accuracy": sum(row["severity_expected"] == row["severity_actual"] for row in rows) / count,
        "extraction_accuracy": sum(row["extraction_success"] for row in rows) / count,
        "evidence_grounding_rate": sum(row["evidence_grounded"] for row in rows) / count,
        "unsupported_claim_count": sum(row["unsupported_claims"] for row in rows),
        "task_completion_rate": sum(row["task_complete"] for row in rows) / count,
        "expected_failure_rejection_rate": sum(row["rejected_as_expected"] for row in failures) / len(failures),
    }}
