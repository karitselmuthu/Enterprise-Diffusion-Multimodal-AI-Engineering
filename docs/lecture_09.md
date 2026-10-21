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

`python experiments/lecture_09/05_benchmark.py` writes `reports/lecture_09.json`. The 26 manually curated synthetic scenarios cover active hazards, equipment faults, negation, resolved and historical events, visual-only inputs, conflicts, and PDF text. Severity accuracy checks expected keyword categories. Extraction success checks that the expected source enters evidence. Grounding checks that findings cite present sources and that cited incident terms occur in those sources. Unsupported-claim count is a narrow, automated proxy; it cannot assess arbitrary VLM statements. Task completion checks for a severity field and at least one evidence source. Tests exercise corrupt inputs and multiple image/text sizes. `06_real_vlm_benchmark.py` separately measures visible-word recall on four dashboard fixtures and records the model's actual text; those outputs remain unverified until human review.

The review API persists pending analyses in SQLite. A reviewer must explicitly approve or reject an incident. Approval requires a summary, recommendation, and evidence citations drawn from the stored analysis. Duplicate decisions are rejected. Configure `REVIEW_API_KEY` and `REVIEW_DB_PATH` through environment variables; the default database is `data/reviews.sqlite3`. The lab uses a shared key, so it does not provide per-reviewer identity assurance or production access control.

The measured local SmolVLM run found the target word in 3 of 4 synthetic dashboards. It missed `PRESSURE HIGH`, returning `Page 1 of 1.` instead. Each CPU request took roughly 105–109 seconds. The model's [official card](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct) describes its architecture and intended image-text use; these lab measurements are specific to this host and four fixtures.
