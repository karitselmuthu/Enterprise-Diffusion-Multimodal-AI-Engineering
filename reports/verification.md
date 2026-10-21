# Verification report

Verified on 21 October 2026 in the project root with Python 3.14 and the declared development dependencies.

| Check | Result |
| --- | --- |
| `python -m pytest -q` | 16 tests passed, covering math, extraction, scenarios, API auth, SQLite persistence, evidence validation and duplicate-decision rejection. |
| Lecture 8 benchmark | 96 training and 32 held-out synthetic sequences; masked reconstruction accuracy 0.618, token error rate 0.382, cross entropy 0.935 nats; four reverse iterations in the sampled run. |
| Lecture 9 scenarios | 26 manually curated synthetic scenarios across nine categories; severity accuracy 25/26 (0.962), extraction success 1.0, evidence grounding 1.0, unsupported-claim count 0, task completion 1.0. The historical-fire case is misclassified as active high severity. |
| Local VLM | Pinned SmolVLM-256M-Instruct snapshot; target status word found in 3/4 synthetic dashboards. The pressure dashboard failed. CPU latency was about 105–109 seconds per image; output remained unverified and did not set severity. |
| Failure cases | Corrupt image, missing document name and unsupported document format rejected. |
| Input-size experiment | 2×2, 20×20 and 100×100 PPM inputs profiled for latency and Python traced peak memory. |
| FastAPI live lab | Controlled reports on a fixed red tile returned undetermined, medium and high severity as expected. |
| Docker | Image built under Colima. In-container smoke check confirmed `/health`, creation and approval of a pending review, and HTTP 409 for a duplicate decision. |

The scenarios are synthetic and have not been independently labeled by domain experts. The visible-word probe and structural grounding checks do not establish general VLM accuracy or factual support. OCR and individual reviewer authentication are outside this lab. Report JSON timings depend on the machine and run.
