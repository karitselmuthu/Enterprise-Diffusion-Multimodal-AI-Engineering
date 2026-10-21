"""Human review terminal for a running API; never auto-approves an incident."""

from __future__ import annotations

import argparse
import json
import os
from urllib.request import Request, urlopen


def request(url: str, key: str, payload: dict | None = None) -> object:
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"X-Review-Key": key}
    if data is not None:
        headers["Content-Type"] = "application/json"
    with urlopen(Request(url, data=data, headers=headers, method="POST" if data else "GET"), timeout=120) as response:
        return json.load(response)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--id", default=None)
    args = parser.parse_args()
    key = os.environ.get("REVIEW_API_KEY")
    if not key:
        raise SystemExit("Set REVIEW_API_KEY before using the review lab")
    base = args.base_url.rstrip("/") + "/reviews"
    if args.id:
        record = request(base + "/" + args.id, key)
    else:
        pending = request(base, key)
        if not pending:
            print("No pending incidents")
            return
        for item in pending:
            print(item["id"], item["created_at"], item["analysis"]["severity"])
        selected = input("Incident ID to review: ").strip()
        record = request(base + "/" + selected, key)
    print(json.dumps(record["analysis"], indent=2))
    sources = [item["source"] for item in record["analysis"]["evidence"]]
    print("Available evidence sources:", ", ".join(sources))
    status = input("Decision (approved/rejected): ").strip()
    reviewer = input("Reviewer ID: ").strip()
    summary = input("Verified summary or rejection reason: ").strip()
    recommendation = input("Recommendation (required for approval): ").strip()
    cited = [value.strip() for value in input("Cited source IDs (comma separated): ").split(",") if value.strip()]
    reviewer_key = os.environ.get("REVIEWER_KEY")
    if not reviewer_key:
        raise SystemExit("Set REVIEWER_KEY to the key assigned to the reviewer")
    outcome = request(base + "/" + record["id"] + "/decision", reviewer_key,
                      {"status": status, "reviewer": reviewer, "summary": summary,
                       "recommendation": recommendation, "cited_sources": cited})
    print(json.dumps({"id": outcome["id"], "status": outcome["status"], "decision": outcome["decision"]}, indent=2))


if __name__ == "__main__":
    main()
