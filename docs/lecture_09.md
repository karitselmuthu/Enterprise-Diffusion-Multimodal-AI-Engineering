# Lecture 9: multimodal experiments

| Phase | Experiment | What it demonstrates |
| --- | --- | --- |
| 9.1 | `01_image_embeddings.py` | Numeric text and image representations. |
| 9.2 | `01_image_embeddings.py` | RGB feature encoding and similarity probes. |
| 9.3 | `02_vision_language.py`, `06_real_vlm_benchmark.py` | Mock backend and cached local image-text-to-text inference. |
| 9.4 | `03_document_processing.py` | UTF-8 and embedded PDF text extraction; optional OCR. |
| 9.5 | `04_cross_modal.py` | Source-linked text, image, and document evidence. |
| 9.6 | `02_vision_language.py` and this comparison | Architectures and model-backed versus feature-backed output. |
| 9.7 | API, `scripts/live_lab.py`, `scripts/review_lab.py` | Incident analysis, persistent review queue, and changing-input lab. |

## Architecture comparison

| Approach | Input handling | Output | Resource cost | Limitation |
| --- | --- | --- | --- | --- |
| RGB feature encoder | Pixel means | Three-number embedding | Tiny | No object, layout, or text understanding. |
| Mock VLM | Pixel statistics | Deterministic description | Tiny | No semantic visual inference. |
| Local image-text-to-text VLM | Image plus text prompt | Generated description | Model dependent | Requires cached weights and memory; output can be unsupported. |
| Document text extraction | UTF-8/PDF text layer | Source text | Low | Scanned PDFs need OCR. |

The optional local backend follows the [Hugging Face image-text-to-text pipeline](https://huggingface.co/docs/transformers/en/tasks/image_text_to_text). `scripts/prepare_local_model.py` downloads an exact snapshot of [SmolVLM-256M-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct) to `data/models/`, which Git ignores. The API accepts `backend: "local"` only when the server has `LOCAL_VLM_MODEL_PATH` configured; clients cannot choose arbitrary model paths. The default Docker image excludes PyTorch. Build with `--build-arg WITH_VLM=true` and mount the model directory for a model-enabled container.

## Evaluation

`python experiments/lecture_09/05_benchmark.py` writes `reports/lecture_09.json`. The 38 manually curated synthetic scenarios cover active hazards, equipment faults, negation, resolved and historical events, recurrence, conflicting clock times, visual-only inputs, conflicts, and PDF text. Severity accuracy checks expected keyword categories. Extraction success checks that the expected source enters evidence. Grounding checks that findings cite present sources and that cited incident terms occur in those sources. Unsupported-claim count is a narrow, automated proxy; it cannot assess arbitrary VLM statements. Task completion checks for a severity field and at least one evidence source. Tests exercise corrupt inputs and multiple image/text sizes. `06_real_vlm_benchmark.py` separately measures visible-word recall on four dashboard fixtures and records the model's actual text; those outputs remain unverified until human review.

`scripts/generate_dashboard_matrix.py` generates 24 varied synthetic dashboards, including small labels, low contrast, alternate layouts and numeric readings. `07_dashboard_matrix.py` scores exact status and reading extraction from the optional local VLM and records each latency. This is synthetic rendered ground truth, not independently labeled visual evidence. `scripts/human_ground_truth.py --export <folder>` prepares blinded packets and two empty reviewer sheets; `--score <reviewer_a.csv> <reviewer_b.csv>` measures agreement and consensus accuracy only after two distinct people fill them. `scripts/reliability_lab.py` probes repeated and concurrent mock API calls, larger images, client timeout, failure recovery, and server RSS snapshots.

After the VLM matrix finishes, `scripts/human_ground_truth.py --export-vlm <folder>` creates a separate sheet for every generated model claim with its source image. `--score-vlm <reviewer_a.csv> <reviewer_b.csv>` measures support agreement once both reviewers inspect the images. The script rejects blank or incomplete labels; no human support score is claimed until they are supplied.

`scripts/acceptance_gate.py` records pass, fail or pending for the six project acceptance criteria. Its temporal percentage applies to the defined synthetic temporal scenarios. The VLM exact-field percentage counts both status and numeric-reading fields across the selected images; a separate both-fields-exact score is also reported. A human evidence gate cannot pass using automated source-link checks alone.

The completed 20-image CPU matrix scored 4/20 exact status values and 6/20 exact readings, or 10/40 fields (25%). Both fields appeared in only 2/20 answers. Mean latency was 122.8 seconds per image, and p95 latency was 140.0 seconds. The 90% extraction target failed. In this free-form-output probe, an exact field means its case- and punctuation-normalized value appears contiguously in the answer; extra text is allowed. This does not establish that extra claims are supported.

The review API persists pending analyses in SQLite. A reviewer must explicitly approve or reject an incident. Approval requires a summary, recommendation, and evidence citations drawn from the stored analysis. Duplicate decisions are rejected. Configure `REVIEW_API_KEY`, `REVIEWER_KEYS_JSON`, and `REVIEW_DB_PATH` through environment variables; the default database is `data/reviews.sqlite3`. Decision identity is bound to a configured reviewer key, though the lab still lacks a managed identity provider and production access control.

The measured local SmolVLM run found the target word in 3 of 4 synthetic dashboards. It missed `PRESSURE HIGH`, returning `Page 1 of 1.` instead. Each CPU request took roughly 105–109 seconds. The model's [official card](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct) describes its architecture and intended image-text use; these lab measurements are specific to this host and four fixtures.
