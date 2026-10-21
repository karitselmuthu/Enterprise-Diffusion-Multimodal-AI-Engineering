import unittest
from pathlib import Path
from io import BytesIO

from src.multimodal.document_parser import extract_document
from src.multimodal.image_processor import load_image, summarize_image
from src.multimodal.incident_analyzer import analyze_incident
from src.multimodal.vision_encoder import cosine_similarity, encode_image, encode_text

SAMPLES = Path(__file__).resolve().parents[2] / "data" / "samples"


class MultimodalTests(unittest.TestCase):
    def test_pixel_features_and_similarity(self):
        image = load_image((SAMPLES / "red_alert.ppm").read_bytes())
        self.assertEqual(summarize_image(image)["dominant_channel"], "red")
        self.assertGreater(cosine_similarity(encode_image(image), encode_text("red")),
                           cosine_similarity(encode_image(image), encode_text("green")))

    def test_text_document_extraction(self):
        result = extract_document((SAMPLES / "incident_note.txt").read_bytes(), "incident_note.txt")
        self.assertIn("pump pressure alarm", result["text"])

    def test_pdf_without_text_is_reported(self):
        from pypdf import PdfWriter
        output = BytesIO()
        writer = PdfWriter()
        writer.add_blank_page(width=100, height=100)
        writer.write(output)
        result = extract_document(output.getvalue(), "scan.pdf")
        self.assertEqual(result["pages"], 1)
        self.assertEqual(result["text"], "")
        self.assertIn("OCR", result["note"])

    def test_negated_smoke_not_high(self):
        result = analyze_incident(text="Pressure alarm. No smoke observed.")
        self.assertEqual(result["severity"], "medium")

    def test_bad_image_and_document_fail(self):
        with self.assertRaises(ValueError):
            load_image(b"not an image")
        with self.assertRaises(ValueError):
            extract_document(b"data", "unknown.bin")


if __name__ == "__main__":
    unittest.main()
