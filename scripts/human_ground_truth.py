"""Export blinded review sheets and score two independent human label files."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.evaluation.multimodal import scenarios, evaluate_scenarios, _asset
from src.multimodal.incident_analyzer import analyze_incident

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("case_id", "reviewer_id", "severity", "all_claims_supported", "notes")
VLM_FIELDS = ("case_id", "reviewer_id", "all_claims_supported", "notes")


def code(identifier: str) -> str:
    return hashlib.sha256(identifier.encode()).hexdigest()[:12]


def export(target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    cases = scenarios()
    with (target / "source_packets.jsonl").open("w") as stream:
        for case in cases:
            analysis = analyze_incident(text=case["report"], image_bytes=_asset(case.get("image")),
                                        document_bytes=_asset(case.get("document")), document_name=case.get("document"))
            stream.write(json.dumps({"case_id": code(case["id"]), "report": case["report"],
                                     "image": case.get("image"), "document": case.get("document"),
                                     "generated_findings": analysis["findings"]}) + "\n")
    for reviewer in ("reviewer_a", "reviewer_b"):
        with (target / f"{reviewer}.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            for case in cases:
                writer.writerow({"case_id": code(case["id"])})


def read_labels(path: Path) -> dict[str, dict]:
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    identifiers = [row["case_id"] for row in rows]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("duplicate case_id")
    for row in rows:
        if row["severity"] not in {"high", "medium", "undetermined"}:
            raise ValueError(f"missing or invalid severity for {row['case_id']}")
        if row["all_claims_supported"] not in {"yes", "no"} or not row["reviewer_id"].strip():
            raise ValueError(f"missing support judgment or reviewer for {row['case_id']}")
    return {row["case_id"]: row for row in rows}


def score(first: Path, second: Path) -> dict:
    a, b = read_labels(first), read_labels(second)
    expected = {code(case["id"]) for case in scenarios()}
    if set(a) != expected or set(b) != expected:
        raise ValueError("both reviewers must label every scenario")
    a_ids = {row["reviewer_id"] for row in a.values()}
    b_ids = {row["reviewer_id"] for row in b.values()}
    if len(a_ids) != 1 or len(b_ids) != 1 or a_ids == b_ids:
        raise ValueError("two distinct reviewer identities are required")
    output = {code(row["scenario"]): row for row in evaluate_scenarios()["scenarios"]}
    agreed = [case for case in expected if a[case]["severity"] == b[case]["severity"]]
    return {"case_count": len(expected), "reviewers": sorted(a_ids | b_ids),
            "severity_agreement": len(agreed) / len(expected),
            "consensus_case_count": len(agreed),
            "model_severity_accuracy_on_consensus": sum(output[case]["severity_actual"] == a[case]["severity"] for case in agreed) / len(agreed) if agreed else None,
            "both_reviewers_claims_supported_rate": sum(a[case]["all_claims_supported"] == b[case]["all_claims_supported"] == "yes" for case in expected) / len(expected),
            "disagreement_ids": sorted(expected - set(agreed)),
            "note": "Claim support is a human yes/no judgment per case; reviewer independence must be verified outside this script."}


def export_vlm(target: Path) -> None:
    report_path = ROOT / "reports/lecture_09_dashboard_matrix.json"
    report = json.loads(report_path.read_text())
    if report["completed"] != report["target"]:
        raise ValueError("complete the VLM matrix before preparing human review")
    target.mkdir(parents=True, exist_ok=True)
    with (target / "vlm_source_packets.jsonl").open("w") as stream:
        for row in report["rows"]:
            stream.write(json.dumps({"case_id": code("vlm:" + row["image"]),
                                     "image": "data/evaluation/dashboard_matrix/" + row["image"],
                                     "generated_claim": row["answer"]}) + "\n")
    for reviewer in ("reviewer_a", "reviewer_b"):
        with (target / f"vlm_{reviewer}.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=VLM_FIELDS, lineterminator="\n")
            writer.writeheader()
            for row in report["rows"]:
                writer.writerow({"case_id": code("vlm:" + row["image"])})


def score_vlm(first: Path, second: Path) -> dict:
    def read(path: Path) -> dict[str, dict]:
        with path.open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        if len({row["case_id"] for row in rows}) != len(rows):
            raise ValueError("duplicate VLM case")
        if any(row["all_claims_supported"] not in {"yes", "no"} or not row["reviewer_id"].strip() for row in rows):
            raise ValueError("every VLM claim needs a reviewer and support judgment")
        return {row["case_id"]: row for row in rows}
    a, b = read(first), read(second)
    report = json.loads((ROOT / "reports/lecture_09_dashboard_matrix.json").read_text())
    expected = {code("vlm:" + row["image"]) for row in report["rows"]}
    if set(a) != expected or set(b) != expected:
        raise ValueError("both reviewers must assess every VLM output")
    a_ids = {row["reviewer_id"] for row in a.values()}
    b_ids = {row["reviewer_id"] for row in b.values()}
    if len(a_ids) != 1 or len(b_ids) != 1 or a_ids == b_ids:
        raise ValueError("two distinct reviewer identities are required")
    agreed = [case for case in expected if a[case]["all_claims_supported"] == b[case]["all_claims_supported"]]
    return {"case_count": len(expected), "support_agreement": len(agreed) / len(expected),
            "both_supported_rate": sum(a[case]["all_claims_supported"] == b[case]["all_claims_supported"] == "yes" for case in expected) / len(expected),
            "disagreement_ids": sorted(expected - set(agreed)),
            "note": "A support judgment requires inspecting the actual image; reviewer independence must be verified outside this script."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--export", type=Path)
    parser.add_argument("--score", nargs=2, type=Path)
    parser.add_argument("--export-vlm", type=Path)
    parser.add_argument("--score-vlm", nargs=2, type=Path)
    args = parser.parse_args()
    if args.export:
        export(args.export)
        print(f"Wrote blinded packets to {args.export}")
    elif args.score:
        print(json.dumps(score(*args.score), indent=2))
    elif args.export_vlm:
        export_vlm(args.export_vlm)
        print(f"Wrote VLM claim packets to {args.export_vlm}")
    elif args.score_vlm:
        print(json.dumps(score_vlm(*args.score_vlm), indent=2))
    else:
        parser.error("choose --export, --score, --export-vlm, or --score-vlm")
