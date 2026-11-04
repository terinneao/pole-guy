import unittest
import os
import sys

# Ensure root directory is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db import (
    init_db,
    get_all_conductors,
    get_conductor_by_code,
    create_conductor,
    update_conductor,
    delete_conductor
)

class TestConductorDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db(force_reseed=True)

    def test_seed_conductors_loaded(self):
        conductors = get_all_conductors()
        self.assertGreaterEqual(len(conductors), 20)
        
        # Check standard conductors exist
        sac_185 = get_conductor_by_code("SAC-185")
        self.assertIsNotNone(sac_185)
        self.assertEqual(sac_185["conductor_type"], "SAC")
        self.assertAlmostEqual(sac_185["breaking_strength_kg"], 3120.0, places=1)

        acsr_477 = get_conductor_by_code("ACSR-477-HAWK")
        self.assertIsNotNone(acsr_477)
        self.assertEqual(acsr_477["conductor_type"], "ACSR")
        self.assertAlmostEqual(acsr_477["breaking_strength_kg"], 8850.0, places=1)

        aac_400 = get_conductor_by_code("AAC-400")
        self.assertIsNotNone(aac_400)
        self.assertEqual(aac_400["conductor_type"], "AAC")
        self.assertEqual(aac_400["cross_section_sqmm"], 400.0)
        self.assertEqual(aac_400["overall_diameter_mm"], 26.0)
        self.assertAlmostEqual(aac_400["weight_kg_per_m"], 1.100, places=3)
        self.assertAlmostEqual(aac_400["breaking_strength_kg"], 6680.0, places=1)

    def test_filter_by_type(self):
        acsr_list = get_all_conductors(conductor_type="ACSR")
        self.assertTrue(all(c["conductor_type"] == "ACSR" for c in acsr_list))
        self.assertGreater(len(acsr_list), 5)

    def test_search_conductors(self):
        results = get_all_conductors(search="Hawk")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["code"], "ACSR-477-HAWK")

    def test_crud_lifecycle(self):
        # Create
        new_data = {
            "code": "TEST-COND-999",
            "name": "Test Experimental Conductor",
            "conductor_type": "ACSR",
            "cross_section_sqmm": 150.0,
            "overall_diameter_mm": 18.0,
            "weight_kg_per_m": 0.55,
            "breaking_strength_kg": 5000.0,
            "standard": "TEST",
            "notes": "Automated unit test record"
        }
        new_id = create_conductor(new_data)
        self.assertIsInstance(new_id, int)

        created = get_conductor_by_code("TEST-COND-999")
        self.assertIsNotNone(created)
        self.assertEqual(created["id"], new_id)

        # Update
        new_data["name"] = "Updated Test Conductor"
        new_data["breaking_strength_kg"] = 5500.0
        update_success = update_conductor(new_id, new_data)
        self.assertTrue(update_success)

        updated = get_conductor_by_code("TEST-COND-999")
        self.assertEqual(updated["name"], "Updated Test Conductor")
        self.assertAlmostEqual(updated["breaking_strength_kg"], 5500.0, places=1)

        # Delete
        delete_success = delete_conductor(new_id)
        self.assertTrue(delete_success)
        self.assertIsNone(get_conductor_by_code("TEST-COND-999"))

if __name__ == "__main__":
    unittest.main()
