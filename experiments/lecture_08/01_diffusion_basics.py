"""Compare continuous Gaussian and discrete absorbing-mask marginals."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
import random
from src.diffusion.noise import linear_beta_schedule, alpha_bars, sample_xt
from src.diffusion.masking import mask_probability, mask_tokens

betas = linear_beta_schedule(5)
bars = alpha_bars(betas)
vector = [1.0, -1.0, 0.5]
tokens = "the pump reports high pressure".split()
print(json.dumps({"continuous": {"equation": "q(x_t|x_0)=N(sqrt(alpha_bar_t)x_0,(1-alpha_bar_t)I)", "alpha_bars": bars, "sample_t5": sample_xt(vector, bars[-1], random.Random(7))}, "discrete": {"equation": "q(x_t|x_0)=(1-t/T)delta_x0+(t/T)delta_MASK", "mask_probability_t3_of_5": mask_probability(3, 5), "sample_t3": mask_tokens(tokens, 0.6, random.Random(7))[0]}}, indent=2))
