# Verification report

Verified on 21 October 2026 in the project root with Python 3.14 and the declared development dependencies.

| Check | Result |
| --- | --- |
| `python -m pytest -q` | 14 tests passed after the PDF extraction fixture was added. |
| Lecture 8 benchmark | 96 training and 32 held-out synthetic sequences; masked reconstruction accuracy 0.618, token error rate 0.382, cross entropy 0.935 nats; four reverse iterations in the sampled run. |
| Lecture 9 scenarios | Five small scenarios; severity accuracy, extraction success, evidence grounding and task completion each 1.0; automated unsupported-claim count 0. |
| Failure cases | Corrupt image, missing document name and unsupported document format rejected. |
| Input-size experiment | 2×2, 20×20 and 100×100 PPM inputs profiled for latency and Python traced peak memory. |
| FastAPI live lab | Controlled reports on a fixed red tile returned undetermined, medium and high severity as expected. |
| Docker | Image built under Colima; `/health` returned `ok` and incident API returned medium for a pressure alarm. |

The tests use tiny deterministic or synthetic inputs. The five scenario scores are pipeline checks, not estimates of field accuracy. A real VLM and OCR executable were not installed or evaluated. Report JSON timings depend on the machine and run.
