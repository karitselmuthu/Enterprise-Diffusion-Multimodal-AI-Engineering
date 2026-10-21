# Enterprise-Diffusion-Multimodal-AI-Engineering
An enterprise-oriented AI engineering platform exploring diffusion language models, masked and iterative generation, multimodal document intelligence, vision-language architectures, model evaluation, and inference performance through modular implementations and reproducible experiments.
# Project overview
  Attribute	Recommendation
  Repository	Enterprise_Diffusion_Multimodal_AI
  Project type	Applied AI architecture and engineering research
  Lecture 8	Diffusion Language Models
  Lecture 9	Multimodal AI & Emerging Architectures
  Primary language	Python
  ML framework	PyTorch
  Model ecosystem	Hugging Face Transformers / Diffusers where applicable
  API	FastAPI
  Testing	pytest
  Deployment	Docker / Colima
  Hardware	Apple Silicon, 8 GB unified memory
  Implementation	Small-model, experiment-driven

# Enterprise problem statement
  Enterprise applications increasingly need to understand information across multiple formats: text, images, screenshots, documents, diagrams, and operational reports.
  Traditional text-only LLM workflows have limitations when important information is contained in visual content. 
  Meanwhile, diffusion-based language modeling offers a different approach to generating and refining text compared with conventional left-to-right autoregressive decoding.

![Proposed solution flow from enterprise incident inputs through Lecture 8 and Lecture 9 to evaluation and human-reviewed incident intelligence](docs/assets/proposed_solution.png)

## Running the application

Run these commands from the repository root with Python 3.11 or newer:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

The interactive API is available at `http://127.0.0.1:8000/docs`. `python scripts/live_lab.py` exercises the running incident endpoint with controlled changes in report text. `docker build -t enterprise-diffusion-multimodal-ai .` builds the API image where Docker or Colima is available.

## Lecture 8 — Diffusion language models

Run `python experiments/lecture_08/01_diffusion_basics.py` through `06_benchmark.py`. The experiments cover Gaussian forward noise, absorbing token masks, masked reconstruction, training a tiny log-linear denoiser, confidence-based iterative unmasking, and comparison with an add-one-smoothed autoregressive bigram model. The core experiments use only the Python standard library. They do not train a continuous reverse process or a PyTorch transformer.

CLI examples:

```bash
python -m cli.main noise
python -m cli.main train --epochs 20
python -m cli.main generate --steps 4 --length 8 --prefix the pump
python -m cli.main benchmark --output reports/lecture_08.json
```

The benchmark uses 96 synthetic training sentences and 32 held-out combinations. It records masked reconstruction accuracy, token error rate, cross entropy, generated samples, latency, Python traced peak memory, and actual generation iterations. See [Lecture 8 notes](docs/lecture_08.md) and the generated [report](reports/lecture_08.json).

API endpoints: `POST /diffusion/mask`, `POST /diffusion/generate`, `POST /diffusion/baseline`, and `GET /diffusion/benchmark`.

## Lecture 9 — Multimodal AI

Run `python experiments/lecture_09/01_image_embeddings.py` through `05_benchmark.py`. The default path uses small PPM dashboard tiles and a text incident note. It measures RGB features and color-text similarity, exercises a deterministic mock VLM, extracts UTF-8 and embedded PDF text, combines source-linked evidence, and evaluates incident scenarios. PNG/JPEG and PDF support use Pillow and pypdf. OCR additionally requires pytesseract and a Tesseract executable.

For actual local VLM inference, install `.[local-vlm]`, place a compatible image-text-to-text model in a local directory, and run `python experiments/lecture_09/02_vision_language.py --model-path /path/to/model`. The local model is optional and is not downloaded by the application. The default mock reports pixel statistics and does not identify objects or hazards.

`POST /multimodal/analyze` accepts JSON with `text`, optional base64 `image_base64`, optional base64 `document_base64` plus `document_name`, and optional `backend`/`model_path`. Example:

```bash
curl -X POST http://127.0.0.1:8000/multimodal/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"Pressure alarm at pump"}'
```

The scenario report measures severity accuracy, extraction success, evidence grounding, unsupported claims, task completion, latency, and Python traced memory. See [Lecture 9 notes](docs/lecture_09.md), the generated [report](reports/lecture_09.json), and [limitations](docs/limitations.md).
