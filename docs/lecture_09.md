# Lecture 9: multimodal experiments

| Phase | Experiment | What it demonstrates |
| --- | --- | --- |
| 9.1 | `01_image_embeddings.py` | Numeric text and image representations. |
| 9.2 | `01_image_embeddings.py` | RGB feature encoding and similarity probes. |
| 9.3 | `02_vision_language.py` | Mock backend and optional local image-text-to-text inference. |
| 9.4 | `03_document_processing.py` | UTF-8 and embedded PDF text extraction; optional OCR. |
| 9.5 | `04_cross_modal.py` | Source-linked text, image, and document evidence. |
| 9.6 | `02_vision_language.py` and this comparison | Architectures and model-backed versus feature-backed output. |
| 9.7 | API and `scripts/live_lab.py` | Incident analysis endpoint and changing-input lab. |

## Architecture comparison

| Approach | Input handling | Output | Resource cost | Limitation |
| --- | --- | --- | --- | --- |
| RGB feature encoder | Pixel means | Three-number embedding | Tiny | No object, layout, or text understanding. |
| Mock VLM | Pixel statistics | Deterministic description | Tiny | No semantic visual inference. |
| Local image-text-to-text VLM | Image plus text prompt | Generated description | Model dependent | Requires cached weights and memory; output can be unsupported. |
| Document text extraction | UTF-8/PDF text layer | Source text | Low | Scanned PDFs need OCR. |

The optional local backend follows the [Hugging Face image-text-to-text pipeline](https://huggingface.co/docs/transformers/en/tasks/image_text_to_text). It requires a compatible model already present on disk. A compact model such as SmolVLM can be used as a separate lab setup, but model weights and their runtime requirements are outside the default installation.

## Evaluation

`python experiments/lecture_09/05_benchmark.py` writes `reports/lecture_09.json`. The first scenarios use a red tile, a green tile, a short document, and incident reports. Severity accuracy checks expected keyword categories. Extraction success checks that the expected source enters evidence. Grounding checks that findings cite present sources and that cited incident terms occur in those sources. Unsupported-claim count is a narrow, automated proxy; it cannot assess arbitrary VLM statements. Task completion checks for a severity field and at least one evidence source. Tests exercise corrupt inputs and multiple image/text sizes.
