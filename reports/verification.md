# Verification report

Verified on 22 October 2026 in the project root with Python 3.14 and the declared development dependencies.

| Check | Result |
| --- | --- |
| `python -m pytest -q` | 20 tests passed, covering math, temporal cases, paired baseline, extraction, scenarios, reviewer identity, SQLite persistence, evidence validation, concurrent and duplicate decisions, and unfilled human-label rejection. |
| Lecture 8 benchmark | 96 training and 32 held-out synthetic sequences; masked reconstruction accuracy 0.618, token error rate 0.382, cross entropy 0.935 nats; four reverse iterations in the sampled run. |
| Lecture 8 paired baseline | 36 settings over three mask ratios, four reverse iteration counts and three seeds. Mean reconstruction accuracy: denoiser 0.613, position-frequency baseline 0.565, using identical held-out masks. |
| Lecture 9 scenarios | 38 manually curated synthetic scenarios, including historical, resolved, recurring and contradictory clock-time reports; severity accuracy 38/38, extraction success 1.0, evidence grounding 1.0, unsupported-claim count 0, task completion 1.0. These labels are not independent ground truth. |
| Local VLM | Pinned SmolVLM-256M-Instruct snapshot; target status word found in 3/4 synthetic dashboards. The pressure dashboard failed. CPU latency was about 105–109 seconds per image; output remained unverified and did not set severity. |
| Exact VLM fields | Twenty selected synthetic dashboards with alternate layouts and small, low-contrast labels. Exact status 4/20 (0.20), exact reading 6/20 (0.30), either field 10/40 (0.25), both fields 2/20 (0.10). Mean CPU latency 122.8 seconds per image; p95 140.0 seconds. The 90% field target failed. |
| Failure cases | Corrupt image, missing document name and unsupported document format rejected. |
| Input-size experiment | 2×2, 20×20 and 100×100 PPM inputs profiled for latency and Python traced peak memory. |
| FastAPI live lab | Controlled reports on a fixed red tile returned undetermined, medium and high severity as expected. |
| Docker | Image built under Colima. In-container smoke check confirmed `/health`, creation and approval of a pending review, and HTTP 409 for a duplicate decision. |
| Live reliability | Ten repeated and four concurrent mock API requests succeeded; a 2,250×1,250 PNG succeeded, 2,700×1,500 was rejected by the pixel limit, a 10 ms client timeout occurred, and a later request recovered. Four simultaneous review decisions produced one approval and three HTTP 409 conflicts; the persisted record was approved. Server RSS snapshots were 59 MB before and 340 MB after, possibly including still-running timed-out work. |
| Human ground truth | Opaque-ID source packets, 20 VLM answer packets, and blank sheets for two reviewers exported. No independent labels or claim-support score yet. |
| Acceptance criteria | Temporal, diffusion comparison, API security and defined reliability workload pass; VLM exact-field extraction fails; human evidence validation remains pending. See `reports/acceptance.json`. |

The scenarios are synthetic and have not been independently labeled by domain experts. Structural grounding checks do not establish factual support for model-generated claims. Reviewer identity uses static per-reviewer keys, not managed user authentication. OCR and server-side cancellation are outside this lab. Report JSON timings depend on the machine and run.
