"""Combine report, dashboard tile and document with source-linked findings."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
from src.multimodal.incident_analyzer import analyze_incident

samples = Path(__file__).resolve().parents[2] / "data/samples"
print(json.dumps(analyze_incident(text="Pressure alarm at pump", image_bytes=(samples / "red_alert.ppm").read_bytes(),
                                  document_bytes=(samples / "incident_note.txt").read_bytes(), document_name="incident_note.txt"), indent=2))
