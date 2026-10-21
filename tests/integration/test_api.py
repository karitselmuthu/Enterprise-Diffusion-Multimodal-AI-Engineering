import unittest
import base64
from pathlib import Path


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from fastapi.testclient import TestClient
            from api.main import app
        except ImportError as exc:
            raise unittest.SkipTest(f"API extras unavailable: {exc}")
        cls.client = TestClient(app)

    def test_health_and_diffusion(self):
        self.assertEqual(self.client.get("/health").json(), {"status": "ok"})
        response = self.client.post("/diffusion/generate", json={"length": 8, "steps": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["tokens"]), 8)

    def test_multimodal_incident_and_validation(self):
        image = (Path(__file__).resolve().parents[2] / "data/samples/red_alert.ppm").read_bytes()
        response = self.client.post("/multimodal/analyze", json={"text": "Smoke by the pump", "image_base64": base64.b64encode(image).decode()})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["severity"], "high")
        self.assertEqual(response.json()["vlm"]["grounding"], "pixel_statistics_only")
        invalid = self.client.post("/multimodal/analyze", json={"image_base64": "%%%"})
        self.assertEqual(invalid.status_code, 422)


if __name__ == "__main__":
    unittest.main()
