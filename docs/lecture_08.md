# Lecture 8: diffusion experiments

Run `python experiments/lecture_08/01_diffusion_basics.py` through `06_benchmark.py` in order, or use `python -m cli.main train`, `generate --steps 4`, and `benchmark`.

The continuous experiment uses Gaussian forward transitions with `beta_t`, `alpha_t = 1-beta_t`, and `alpha_bar_t = product(alpha_s)`. Its direct marginal is `q(x_t|x_0) = N(sqrt(alpha_bar_t)x_0, (1-alpha_bar_t)I)`. This is a forward noising demonstration; there is no trained continuous reverse model.

The discrete experiment uses an absorbing `[MASK]` state. At normalized time `t/T`, each original token is independently replaced with probability `t/T`. The denoiser is a trainable log-linear classifier with token-position, nearest-visible-neighbor and visible bag features. It minimizes masked-token cross entropy by stochastic gradient updates. It is deliberately tiny and does not implement a transformer.

Reverse generation starts with masked slots, predicts every masked position in parallel, and commits the highest-confidence sampled positions over the requested number of iterations. The autoregressive baseline is an add-one-smoothed bigram model trained on the same 96 synthetic sentences. The 32 held-out sentences use unseen combinations of familiar vocabulary. The benchmark reports held-out masked-token accuracy and cross entropy, illustrative generated text, one generation latency sample, Python traced peak allocation, and actual iteration count. These are educational measurements, not statistically stable or comparable language-quality scores.
