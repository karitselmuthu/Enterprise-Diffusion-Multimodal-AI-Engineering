"""Train the tiny masked denoiser and save it under reports/."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
from src.evaluation.runner import train_default

model, train, test, losses = train_default()
target = Path(__file__).resolve().parents[2] / "reports" / "tiny_denoiser.json"
model.save(target)
print(json.dumps({"model": str(target), "train_examples": len(train), "held_out_examples": len(test), "loss_by_epoch": losses}, indent=2))
