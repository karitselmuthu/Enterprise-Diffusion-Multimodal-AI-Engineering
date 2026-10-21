"""Exercise health and one full review decision inside a running API container."""

from __future__ import annotations

import json
import os
import time
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:8000"


def call(path: str, payload: dict | None = None, *, reviewer: bool = False) -> tuple[int, dict]:
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"X-Review-Key": os.environ["REVIEW_API_KEY"]}
    if reviewer:
        headers["X-Reviewer-Key"] = os.environ["REVIEWER_SMOKE_KEY"]
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = Request(BASE + path, data=data, headers=headers, method="POST" if data else "GET")
    try:
        with urlopen(request, timeout=10) as response:
            return response.status, json.load(response)
    except HTTPError as exc:
        return exc.code, json.load(exc)


def main() -> None:
    for attempt in range(20):
        try:
            health_status, health = call("/health")
            break
        except URLError:
            if attempt == 19:
                raise
            time.sleep(0.5)
    assert health_status == 200 and health["status"] == "ok"
    create_status, incident = call("/reviews", {"text": "Smoke in server room"})
    assert create_status == 201 and incident["status"] == "pending"
    decision = {"status": "approved", "reviewer": "container-smoke", "summary": "Smoke reported",
                "recommendation": "Verify the site alert", "cited_sources": ["report_text"]}
    decision_path = f"/reviews/{incident['id']}/decision"
    approved_status, approved = call(decision_path, decision, reviewer=True)
    assert approved_status == 200 and approved["status"] == "approved"
    duplicate_status, _ = call(decision_path, decision, reviewer=True)
    assert duplicate_status == 409
    print(json.dumps({"health": health["status"], "review": approved["status"],
                      "duplicate_decision_status": duplicate_status}))


if __name__ == "__main__":
    main()
