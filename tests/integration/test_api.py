import unittest
import base64
from pathlib import Path
import os
import tempfile
from unittest.mock import patch


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

    def test_review_auth_persistence_and_single_decision(self):
        with patch.dict(os.environ, {"REVIEW_API_KEY": ""}):
            self.assertEqual(self.client.get("/reviews").status_code, 503)
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"REVIEW_API_KEY": "test-key", "REVIEWER_KEYS_JSON": '{"analyst":"analyst-key"}', "REVIEW_DB_PATH": str(Path(folder) / "reviews.sqlite3")}):
            self.assertEqual(self.client.get("/reviews").status_code, 401)
            headers = {"X-Review-Key": "test-key"}
            reviewer_headers = {**headers, "X-Reviewer-Key": "analyst-key"}
            created = self.client.post("/reviews", json={"text": "Smoke in server room"}, headers=headers)
            self.assertEqual(created.status_code, 201)
            record = created.json()
            self.assertEqual(record["status"], "pending")
            self.assertEqual(len(self.client.get("/reviews", headers=headers).json()), 1)
            invalid = self.client.post(f"/reviews/{record['id']}/decision", headers=headers,
                                       json={"status": "approved", "reviewer": "analyst", "summary": "Smoke reported",
                                             "recommendation": "Inspect", "cited_sources": ["unknown"]})
            self.assertEqual(invalid.status_code, 401)
            decision = {"status": "approved", "reviewer": "analyst", "summary": "Smoke reported",
                        "recommendation": "Inspect the room", "cited_sources": ["report_text"]}
            with patch.dict(os.environ, {"REVIEWER_KEYS_JSON": ""}):
                self.assertEqual(self.client.post(f"/reviews/{record['id']}/decision", headers=reviewer_headers, json=decision).status_code, 503)
            self.assertEqual(self.client.post(f"/reviews/{record['id']}/decision", headers={**headers, "X-Reviewer-Key": "wrong"}, json=decision).status_code, 401)
            self.assertEqual(self.client.post(f"/reviews/{record['id']}/decision", headers=reviewer_headers, json={**decision, "reviewer": "someone-else"}).status_code, 403)
            self.assertEqual(self.client.post("/reviews/not-a-valid-id/decision", headers=reviewer_headers, json=decision).status_code, 404)
            self.assertEqual(self.client.post(f"/reviews/{record['id']}/decision", headers=reviewer_headers,
                                              json={**decision, "cited_sources": ["unknown"]}).status_code, 422)
            approved = self.client.post(f"/reviews/{record['id']}/decision", headers=reviewer_headers, json=decision)
            self.assertEqual(approved.status_code, 200)
            self.assertEqual(approved.json()["status"], "approved")
            self.assertEqual(self.client.post(f"/reviews/{record['id']}/decision", headers=reviewer_headers, json=decision).status_code, 409)
            rejected = self.client.post("/reviews", json={"text": "Check rack"}, headers=headers).json()
            reject_body = {"status": "rejected", "reviewer": "analyst", "summary": "Insufficient evidence", "cited_sources": []}
            self.assertEqual(self.client.post(f"/reviews/{rejected['id']}/decision", headers=reviewer_headers, json=reject_body).json()["status"], "rejected")
            self.assertEqual(self.client.post(f"/reviews/{rejected['id']}/decision", headers=reviewer_headers, json=decision).status_code, 409)


if __name__ == "__main__":
    unittest.main()
