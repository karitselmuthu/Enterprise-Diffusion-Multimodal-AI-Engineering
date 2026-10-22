"""Exercise live mock API request bursts and measure server resident memory."""

from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time

import httpx
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def rss_bytes(pid: int) -> int:
    return int(subprocess.check_output(["ps", "-o", "rss=", "-p", str(pid)], text=True).strip()) * 1024


def main() -> None:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    review_db = Path(tempfile.gettempdir()) / f"reliability_lab_reviews_{os.getpid()}.sqlite3"
    process = subprocess.Popen([sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", str(port)],
                               cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               env={**os.environ, "REVIEW_DB_PATH": str(review_db), "REVIEW_API_KEY": "lab-queue-key",
                                    "REVIEWER_KEYS_JSON": '{"lab-reviewer":"lab-decision-key"}'})
    base = f"http://127.0.0.1:{port}"
    try:
        for _ in range(100):
            try:
                if httpx.get(base + "/health", timeout=1).status_code == 200:
                    break
            except httpx.RequestError:
                time.sleep(0.1)
        else:
            raise RuntimeError("API did not start")
        rss_before = rss_bytes(process.pid)
        source = Image.open(ROOT / "data/evaluation/pressure_dashboard.png")
        payloads = []
        for scale in (1, 2, 2.5, 3):
            image = source.resize((int(source.width * scale), int(source.height * scale)))
            stream = BytesIO()
            image.save(stream, format="PNG")
            payloads.append({"text": "Pressure alarm active", "image_base64": base64.b64encode(stream.getvalue()).decode()})

        def request(payload: dict) -> dict:
            start = time.perf_counter()
            response = httpx.post(base + "/multimodal/analyze", json=payload, timeout=30)
            return {"status": response.status_code, "latency_ms": (time.perf_counter() - start) * 1000}

        repeated = [request(payloads[0]) for _ in range(10)]
        with ThreadPoolExecutor(max_workers=4) as executor:
            concurrent = list(executor.map(request, [payloads[1]] * 4))
        larger = request(payloads[2])
        oversized = request(payloads[3])
        malformed = request({"text": "check", "image_base64": "%%%"})
        try:
            httpx.post(base + "/multimodal/analyze", json=payloads[2], timeout=0.01)
            timeout_observed = False
        except httpx.TimeoutException:
            timeout_observed = True
        recovery = request(payloads[0])
        queue_headers = {"X-Review-Key": "lab-queue-key"}
        decision_headers = {**queue_headers, "X-Reviewer-Key": "lab-decision-key"}
        created = httpx.post(base + "/reviews", json={"text": "Smoke active in rack room"}, headers=queue_headers, timeout=30)
        assert created.status_code == 201
        review_id = created.json()["id"]
        decision = {"status": "approved", "reviewer": "lab-reviewer", "summary": "Smoke is reported",
                    "recommendation": "Inspect rack room", "cited_sources": ["report_text"]}
        decision_url = base + f"/reviews/{review_id}/decision"
        with ThreadPoolExecutor(max_workers=4) as executor:
            decisions = list(executor.map(lambda _: httpx.post(decision_url, json=decision,
                                                               headers=decision_headers, timeout=30).status_code, range(4)))
        final_review = httpx.get(base + f"/reviews/{review_id}", headers=queue_headers, timeout=30).json()
        rss_after = rss_bytes(process.pid)
        assert all(row["status"] == 200 for row in repeated + concurrent + [larger, recovery])
        assert malformed["status"] == 422 and oversized["status"] == 422, (malformed, oversized)
        assert timeout_observed
        assert sorted(decisions) == [200, 409, 409, 409]
        assert final_review["status"] == "approved" and final_review["decision"]["reviewer"] == "lab-reviewer"
        report = {"repeated": repeated, "concurrent": concurrent, "larger": larger,
                  "oversized": oversized, "malformed": malformed, "client_timeout_observed": timeout_observed,
                  "recovery": recovery,
                  "simultaneous_review_decisions": decisions, "final_review_status": final_review["status"],
                  "image_sizes": [[int(900 * scale), int(500 * scale)] for scale in (1, 2, 2.5, 3)],
                  "server_rss_before_bytes": rss_before, "server_rss_after_bytes": rss_after,
                  "note": "Mock backend only; OS RSS snapshots are process-level, not request peaks. A client timeout does not cancel server computation. VLM timeouts are not tested."}
        target = ROOT / "reports/reliability_lab.json"
        target.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({"report": str(target), "statuses": [row["status"] for row in concurrent],
                          "rss_before": rss_before, "rss_after": rss_after}))
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        review_db.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
