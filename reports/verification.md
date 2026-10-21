# Verification report

Verified on 21 October 2026 in the project root with Python 3.14 and the declared development dependencies.

| Check | Result |
| --- | --- |
| `python -m pytest -q` | 20 tests passed, covering math, temporal cases, paired baseline, extraction, scenarios, reviewer identity, SQLite persistence, evidence validation, concurrent and duplicate decisions, and unfilled human-label rejection. |
| Lecture 8 benchmark | 96 training and 32 held-out synthetic sequences; masked reconstruction accuracy 0.618, token error rate 0.382, cross entropy 0.935 nats; four reverse iterations in the sampled run. |
| Lecture 8 paired baseline | 36 settings over three mask ratios, four reverse iteration counts and three seeds. Mean reconstruction accuracy: denoiser 0.613, position-frequency baseline 0.565, using identical held-out masks. |
| Lecture 9 scenarios | 38 manually curated synthetic scenarios, including historical, resolved, recurring and contradictory clock-time reports; severity accuracy 38/38, extraction success 1.0, evidence grounding 1.0, unsupported-claim count 0, task completion 1.0. These labels are not independent ground truth. |
| Local VLM | Pinned SmolVLM-256M-Instruct snapshot; target status word found in 3/4 synthetic dashboards. The pressure dashboard failed. CPU latency was about 105–109 seconds per image; output remained unverified and did not set severity. |
| Failure cases | Corrupt image, missing document name and unsupported document format rejected. |
| Input-size experiment | 2×2, 20×20 and 100×100 PPM inputs profiled for latency and Python traced peak memory. |
| FastAPI live lab | Controlled reports on a fixed red tile returned undetermined, medium and high severity as expected. |
| Docker | Image built under Colima. In-container smoke check confirmed `/health`, creation and approval of a pending review, and HTTP 409 for a duplicate decision. |
| Live reliability | Ten repeated and four concurrent mock API requests succeeded; a 2,250×1,250 PNG succeeded, 2,700×1,500 was rejected by the pixel limit, a 10 ms client timeout occurred, and a later request recovered. Server RSS snapshots were 59 MB before and 367 MB after, possibly including still-running timed-out work. |
| Human ground truth | Opaque-ID source packets and two blank reviewer sheets exported. No independent labels or claim-support score yet. |

The scenarios are synthetic and have not been independently labeled by domain experts. The visible-word probe and structural grounding checks do not establish general VLM accuracy or factual support. OCR and individual reviewer authentication are outside this lab. Report JSON timings depend on the machine and run.
