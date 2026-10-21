"""Inspect noise accumulation across timesteps."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
import random
from src.diffusion.noise import linear_beta_schedule, sample_chain

states = sample_chain([1.0, 0.0, -1.0], linear_beta_schedule(10), random.Random(7))
print(json.dumps({"states": states, "squared_distance_from_start": [sum((x-y)**2 for x,y in zip(state, states[0])) for state in states]}, indent=2))
