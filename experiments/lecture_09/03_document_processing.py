"""Extract synthetic document text; accepts an optional external PDF path."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import argparse
import json
from src.multimodal.document_parser import extract_document

parser = argparse.ArgumentParser()
parser.add_argument("path", nargs="?", type=Path, default=Path(__file__).resolve().parents[2] / "data/samples/incident_note.txt")
args = parser.parse_args()
print(json.dumps(extract_document(args.path.read_bytes(), args.path.name), indent=2))
