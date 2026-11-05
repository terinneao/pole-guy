import unittest
import json
import os
import sys

# Ensure root directory is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

class TestAPIResilience(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_calculate_null_fields_resilience(self):
        """Verify that null/empty/corrupted conductor and guy wire inputs never raise 500."""
        payload = {
            "pole": None,
            "anchor": None,
            "guy_wire_spec": None,
            "conductors": [
                {
                    "level": 1,
                    "enabled": True,
                    "height_m": None,
                    "weight_kg_per_m": None,
                    "breaking_strength_kg": None,
                    "span_m": "",
                    "sag_m": None,
                    "wind_pressure_kg_m2": None
                }
            ],
            "overhead_ground_wire": {
                "enabled": True,
                "height_m": "",
                "span_m": None,
                "sag_m": "",
                "wind_pressure_kg_m2": None
            },
            "guy_wires": [
                {
                    "level": 1,
                    "enabled": True,
                    "height_m": None,
                    "anchor_distance_m": "",
                    "size_sqmm": None
                }
            ]
        }
        res = self.client.post("/api/calculate", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("summary", data["data"])

    def test_calculate_malformed_json_returns_400_not_500(self):
        """Verify that malformed or non-dict payloads return 400 Bad Request, not 500."""
        # Non-dict payload
        res = self.client.post("/api/calculate", data=json.dumps([1, 2, 3]), content_type="application/json")
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.get_json()["success"])

        # Empty body
        res = self.client.post("/api/calculate", data="", content_type="application/json")
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.get_json()["success"])

    def test_conductor_crud_error_handling(self):
        """Verify conductor endpoints handle errors gracefully."""
        # Missing required field -> 400
        res = self.client.post("/api/conductors", data=json.dumps({"code": "TEST"}), content_type="application/json")
        self.assertEqual(res.status_code, 400)

        # Invalid ID -> 404
        res = self.client.get("/api/conductors/99999999")
        self.assertEqual(res.status_code, 404)

        # Reset works
        res = self.client.post("/api/conductors/reset")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

if __name__ == "__main__":
    unittest.main()
