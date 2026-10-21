"""Demonstrate forward masking and explicit reconstruction."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
import random
from src.diffusion.masking import mask_tokens, reconstruct

original = "the sensor in east reports high temperature".split()
masked, positions = mask_tokens(original, 0.5, random.Random(7), ensure_one=True)
print(json.dumps({"original": original, "masked": masked, "positions": positions, "reconstructed": reconstruct(masked, {i: original[i] for i in positions})}, indent=2))
