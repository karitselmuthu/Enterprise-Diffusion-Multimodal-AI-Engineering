"""Compare interpretable image and text color representations."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
from src.multimodal.image_processor import load_image, summarize_image
from src.multimodal.vision_encoder import encode_image, encode_text, cosine_similarity

samples = Path(__file__).resolve().parents[2] / "data" / "samples"
results = {}
for name in ("red_alert.ppm", "green_status.ppm"):
    image = load_image((samples / name).read_bytes())
    embedding = encode_image(image)
    results[name] = {"summary": summarize_image(image), "embedding": embedding,
                     "red_similarity": cosine_similarity(embedding, encode_text("red")),
                     "green_similarity": cosine_similarity(embedding, encode_text("green"))}
print(json.dumps(results, indent=2))
