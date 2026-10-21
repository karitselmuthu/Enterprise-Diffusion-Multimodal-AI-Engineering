import unittest

from src.evaluation.metrics import profile
from src.multimodal.image_processor import load_image
from src.multimodal.incident_analyzer import analyze_incident


class PerformanceShapeTests(unittest.TestCase):
    def test_multiple_image_sizes(self):
        for width in (2, 20, 100):
            pixels = " ".join(["255 0 0"] * (width * width))
            data = f"P3\n{width} {width}\n255\n{pixels}\n".encode()
            measured = profile(lambda: load_image(data))
            self.assertEqual(measured["result"].width, width)
            self.assertGreaterEqual(measured["latency_ms"], 0)
            self.assertGreater(measured["peak_traced_bytes"], 0)

    def test_multiple_text_sizes(self):
        for repetitions in (1, 10, 100):
            measured = profile(lambda: analyze_incident(text="pressure alarm " * repetitions))
            self.assertEqual(measured["result"]["severity"], "medium")


if __name__ == "__main__":
    unittest.main()
