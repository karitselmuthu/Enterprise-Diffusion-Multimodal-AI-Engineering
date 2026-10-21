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
    process = subprocess.Popen([sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", str(port)],
                               cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               env={**os.environ, "REVIEW_DB_PATH": str(Path(tempfile.gettempdir()) / "reliability_lab_reviews.sqlite3")})
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
        rss_after = rss_bytes(process.pid)
        assert all(row["status"] == 200 for row in repeated + concurrent + [larger, recovery])
        assert malformed["status"] == 422 and oversized["status"] == 422, (malformed, oversized)
        assert timeout_observed
        report = {"repeated": repeated, "concurrent": concurrent, "larger": larger,
                  "oversized": oversized, "malformed": malformed, "client_timeout_observed": timeout_observed,
                  "recovery": recovery,
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


if __name__ == "__main__":
    main()
