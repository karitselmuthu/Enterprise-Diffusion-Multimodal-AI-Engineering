# Architecture

```mermaid
flowchart LR
  CLI[CLI and experiment scripts] --> D[Diffusion core]
  CLI --> M[Multimodal core]
  API[FastAPI routes] --> D
  API --> M
  D --> E[Evaluation and JSON reports]
  M --> E
  M --> MOCK[Deterministic mock VLM]
  M --> LOCAL[Optional cached local VLM]
```

The diffusion core has independent continuous-noise demonstrations and a discrete masked-token path. The latter trains a small log-linear classifier and reconstructs tokens in configurable reverse iterations. The autoregressive bigram baseline uses the same synthetic training split.

The multimodal core decodes images, computes RGB features, extracts text from documents, and records source-linked findings. The default VLM backend is a deterministic pixel-statistics mock. An optional local Hugging Face image-text-to-text pipeline can generate natural-language descriptions from a cached model. The incident analyzer keeps the backend output separate from rule-based severity so model-generated text cannot silently set severity.

The API uses JSON with bounded base64 binary inputs. `GET /health` is a minimal runtime check. The Docker image serves the API on port 8000. CI installs dependencies, runs pytest and a Lecture 8 benchmark, then builds the image.
