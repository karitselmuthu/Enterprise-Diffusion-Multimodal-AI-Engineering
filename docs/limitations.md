# Limitations and expansion plan

- The continuous diffusion experiment models only forward Gaussian noise. It does not train or sample a reverse continuous diffusion model.
- The masked denoiser is a tiny log-linear classifier on templated text, not a neural diffusion language model. It may generate awkward or repeated tokens. The autoregressive baseline is a bigram model. Their single-sample latency comparison is illustrative.
- The default image embedding captures RGB means only. Image color similarity is not semantic similarity; it cannot read dashboard labels or diagrams.
- The default VLM is a pixel-statistics mock. Real local inference requires a compatible cached model, PyTorch and Transformers. The model is outside default CI; the optional four-image benchmark is a narrow visual-text probe, not broad validation.
- The measured local model missed a large `PRESSURE HIGH` label in one of four synthetic dashboards and took about 105–109 seconds per image on this CPU-only host. It is not suitable for interactive incident triage here without a faster runtime and more evaluation.
- PDF extraction reads embedded text. Scanned PDFs need OCR; OCR quality varies by layout and image quality.
- Keyword-based severity can miss synonyms, context and long reports. It is a triage experiment, not an operational incident decision. A visible red tile alone never raises severity.
- Automated grounding checks verify evidence links and cited incident terms. They do not fully verify claims from a real VLM.
- The 38 manually curated scenarios are synthetic and have not been independently labeled by domain experts. The new clause-level timeline heuristic handles the supplied historical, resolved and recurrence examples, but it is not a general temporal reasoner.
- Review decisions require a reviewer-specific static key, but key possession is not strong identity assurance. SQLite records are not encrypted at rest and there are no production retention or access policies.
- `tracemalloc` reports Python allocations; the reliability lab adds OS process RSS snapshots but does not capture native or GPU memory peaks per request. Timing is a small local sample, not a service-level latency guarantee. A client timeout does not cancel server computation.

The proposed later dataset targets are 1,000 short texts, 5,000 masked training examples, 100 incident descriptions, 50 screenshots, 30 diagrams, 50 documents and 100 scenarios. Expand only after the small fixture pipeline and evaluation rules are stable. Add representative human-labeled cases and separate train/test sources before interpreting quality scores as general performance.
