"""Generate the same length with different reverse iteration budgets."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
from src.diffusion.generator import generate
from src.evaluation.runner import train_default

model, _, _, _ = train_default()
print(json.dumps({str(steps): generate(model, length=8, steps=steps, prefix=["the", "pump"], seed=7) for steps in (1, 2, 4, 8)}, indent=2))
