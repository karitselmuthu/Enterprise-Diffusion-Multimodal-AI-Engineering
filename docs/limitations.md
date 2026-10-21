# Limitations and expansion plan

- The continuous diffusion experiment models only forward Gaussian noise. It does not train or sample a reverse continuous diffusion model.
- The masked denoiser is a tiny log-linear classifier on templated text, not a neural diffusion language model. It may generate awkward or repeated tokens. The autoregressive baseline is a bigram model. Their single-sample latency comparison is illustrative.
- The default image embedding captures RGB means only. Image color similarity is not semantic similarity; it cannot read dashboard labels or diagrams.
- The default VLM is a pixel-statistics mock. Real local inference requires a compatible cached model, PyTorch and Transformers. It was not validated in the default automated suite.
- PDF extraction reads embedded text. Scanned PDFs need OCR; OCR quality varies by layout and image quality.
- Keyword-based severity can miss synonyms, context and long reports. It is a triage experiment, not an operational incident decision. A visible red tile alone never raises severity.
- Automated grounding checks verify evidence links and cited incident terms. They do not fully verify claims from a real VLM.
- `tracemalloc` reports Python allocations; it does not include all native library, model, GPU or process memory. Timing is a small local sample, not a service-level latency guarantee.

The proposed later dataset targets are 1,000 short texts, 5,000 masked training examples, 100 incident descriptions, 50 screenshots, 30 diagrams, 50 documents and 100 scenarios. Expand only after the small fixture pipeline and evaluation rules are stable. Add representative human-labeled cases and separate train/test sources before interpreting quality scores as general performance.
