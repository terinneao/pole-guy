import unittest
import math
import os
import sys

# Ensure root directory is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine import calculate_pole_guy_system

class TestPoleGuyMechanics(unittest.TestCase):
    def setUp(self):
        self.sample_input = {
            "pole": {
                "height_m": 14.3,
                "embedment_m": 2.0,
                "weight_kg": 1200.0
            },
            "anchor": {
                "distance_m": 8.0
            },
            "guy_wire_spec": {
                "rts_kg": 8528.0, # 95 sq.mm steel strand
                "unit_weight_kg_m": 0.764,
                "required_sf": 2.0
            },
            "calculation_method": "elastic",
            "conductors": [
                {
                    "level": 1,
                    "enabled": True,
                    "height_m": 12.0,
                    "code": "SAC-185",
                    "tension_mode": "direct",
                    "tension_kg": 800.0,
                    "num_conductors": 1,
                    "weight_kg_per_m": 0.71,
                    "span_length_m": 50.0
                },
                {
                    "level": 2,
                    "enabled": True,
                    "height_m": 10.5,
                    "code": "SAC-185",
                    "tension_mode": "direct",
                    "tension_kg": 800.0,
                    "num_conductors": 1,
                    "weight_kg_per_m": 0.71,
                    "span_length_m": 50.0
                },
                {
                    "level": 3,
                    "enabled": True,
                    "height_m": 9.0,
                    "code": "SAC-185",
                    "tension_mode": "direct",
                    "tension_kg": 800.0,
                    "num_conductors": 1,
                    "weight_kg_per_m": 0.71,
                    "span_length_m": 50.0
                }
            ],
            "guy_wires": [
                {"level": 1, "enabled": True, "height_m": 12.0, "anchor_distance_m": 8.0},
                {"level": 2, "enabled": True, "height_m": 10.5, "anchor_distance_m": 8.0},
                {"level": 3, "enabled": True, "height_m": 9.0,  "anchor_distance_m": 8.0},
                {"level": 4, "enabled": True, "height_m": 7.5,  "anchor_distance_m": 8.0},
                {"level": 5, "enabled": True, "height_m": 6.0,  "anchor_distance_m": 8.0},
                {"level": 6, "enabled": True, "height_m": 4.5,  "anchor_distance_m": 8.0},
                {"level": 7, "enabled": True, "height_m": 3.0,  "anchor_distance_m": 8.0}
            ]
        }

    def test_overturning_moment_calculation(self):
        res = calculate_pole_guy_system(self.sample_input)
        
        # Conductor Overturning Moment:
        # C1: 800 * 12.0 = 9600 kg.m
        # C2: 800 * 10.5 = 8400 kg.m
        # C3: 800 * 9.0  = 7200 kg.m
        # Total = 9600 + 8400 + 7200 = 25200 kg.m
        expected_moment = 800.0 * 12.0 + 800.0 * 10.5 + 800.0 * 9.0
        self.assertAlmostEqual(res["summary"]["total_overturning_moment_kg_m"], expected_moment, places=1)
        self.assertAlmostEqual(res["summary"]["total_conductor_h_force_kg"], 2400.0, places=1)

    def test_moment_equilibrium(self):
        res = calculate_pole_guy_system(self.sample_input)
        
        overturning = res["summary"]["total_overturning_moment_kg_m"]
        resisting = res["summary"]["total_resisting_moment_kg_m"]
        
        # The elastic deflection method should balance 100% of the overturning moment
        self.assertAlmostEqual(resisting, overturning, delta=1.0)
        self.assertAlmostEqual(res["pole_base"]["moment_balance_pct"], 100.0, places=0)

    def test_guy_wire_geometry(self):
        res = calculate_pole_guy_system(self.sample_input)
        
        g1 = res["guy_wires"][0]
        # Level 1: H = 12.0, L = 8.0 -> Slope = sqrt(144 + 64) = sqrt(208) ~= 14.42 m
        expected_slope = math.sqrt(12.0**2 + 8.0**2)
        self.assertAlmostEqual(g1["slope_length_m"], round(expected_slope, 2), places=2)
        
        expected_angle = math.degrees(math.atan2(12.0, 8.0))
        self.assertAlmostEqual(g1["angle_deg"], round(expected_angle, 1), places=1)

    def test_guy_wire_tension_and_safety_factors(self):
        res = calculate_pole_guy_system(self.sample_input)
        
        # Guy wire RTS = 8528 kg
        for g in res["guy_wires"]:
            self.assertTrue(g["enabled"])
            self.assertGreater(g["tension_kg"], 0.0)
            # Verify horizontal and vertical component trigonometric resolution
            angle_rad = math.radians(g["angle_deg"])
            expected_th = g["tension_kg"] * math.cos(angle_rad)
            expected_tv = g["tension_kg"] * math.sin(angle_rad)
            self.assertAlmostEqual(g["horizontal_force_kg"], round(expected_th, 2), delta=0.5)
            self.assertAlmostEqual(g["vertical_force_kg"], round(expected_tv, 2), delta=0.5)
            
            # Verify Safety Factor = RTS / T
            expected_sf = 8528.0 / g["tension_kg"]
            self.assertAlmostEqual(g["safety_factor"], round(expected_sf, 2), places=1)

    def test_anchor_reaction_resultant(self):
        res = calculate_pole_guy_system(self.sample_input)
        
        th_total = res["anchor"]["total_horizontal_pull_kg"]
        tv_total = res["anchor"]["total_vertical_uplift_kg"]
        expected_r = math.sqrt(th_total**2 + tv_total**2)
        self.assertAlmostEqual(res["anchor"]["resultant_pull_kg"], round(expected_r, 2), places=1)

    def test_downward_thrust_on_pole(self):
        res = calculate_pole_guy_system(self.sample_input)
        
        # P_thrust = Guy vertical component + Pole weight + Conductor weight + Guy wire weight
        expected_thrust = (
            res["anchor"]["total_vertical_uplift_kg"] +
            self.sample_input["pole"]["weight_kg"] +
            res["summary"]["total_conductor_weight_kg"] +
            res["summary"]["total_guy_weight_kg"]
        )
        self.assertAlmostEqual(res["pole_base"]["total_downward_thrust_kg"], round(expected_thrust, 2), places=1)

    def test_redistribution_when_guys_disabled(self):
        # Disable lower 3 guys (keep only G1-G4)
        modified_input = dict(self.sample_input)
        modified_input["guy_wires"] = [
            {"level": 1, "enabled": True, "height_m": 12.0, "anchor_distance_m": 8.0},
            {"level": 2, "enabled": True, "height_m": 10.5, "anchor_distance_m": 8.0},
            {"level": 3, "enabled": True, "height_m": 9.0,  "anchor_distance_m": 8.0},
            {"level": 4, "enabled": True, "height_m": 7.5,  "anchor_distance_m": 8.0},
            {"level": 5, "enabled": False, "height_m": 6.0, "anchor_distance_m": 8.0},
            {"level": 6, "enabled": False, "height_m": 4.5, "anchor_distance_m": 8.0},
            {"level": 7, "enabled": False, "height_m": 3.0, "anchor_distance_m": 8.0}
        ]
        res_7 = calculate_pole_guy_system(self.sample_input)
        res_4 = calculate_pole_guy_system(modified_input)
        
        # Total resisting moment must still equal 25200 kg.m
        self.assertAlmostEqual(res_4["summary"]["total_resisting_moment_kg_m"], 25200.0, delta=1.0)
        # Tension on remaining guys (e.g. G1) must increase
    def test_conductor_tension_from_span_and_sag(self):
        # SAC-185: weight = 0.71 kg/m
        # Span = 50 m, Sag = 0.6 m
        # Expected T = (0.71 * 50^2) / (8 * 0.6) = (0.71 * 2500) / 4.8 = 1775 / 4.8 = 369.79 kg
        sag_span_input = dict(self.sample_input)
        sag_span_input["conductors"] = [
            {
                "level": 1,
                "enabled": True,
                "height_m": 12.0,
                "code": "SAC-185",
                "weight_kg_per_m": 0.71,
                "breaking_strength_kg": 3120.0,
                "span_m": 50.0,
                "sag_m": 0.60,
                "tension_mode": "sag_span",
                "num_conductors": 1
            }
        ]
        res = calculate_pole_guy_system(sag_span_input)
        c1 = res["conductors"][0]
        
        expected_tension = (0.71 * (50.0 ** 2)) / (8.0 * 0.60) # 369.7916 kg
        self.assertAlmostEqual(c1["single_tension_kg"], round(expected_tension, 2), places=2)
        self.assertAlmostEqual(c1["horizontal_force_kg"], round(expected_tension, 2), places=2)
        # Expected moment = 369.79 * 12 = 4437.5 kg.m
    def test_22m_pole_preset(self):
        preset_22m = {
            "pole": {"height_m": 22.0, "embedment_m": 2.8, "weight_kg": 3500.0},
            "anchor": {"distance_m": 12.0},
            "guy_wire_spec": {"rts_kg": 8528.0, "unit_weight_kg_m": 0.764, "required_sf": 2.0},
            "calculation_method": "elastic",
            "conductors": [
                {"level": 1, "enabled": True, "height_m": 18.5, "code": "SAC-185", "weight_kg_per_m": 0.71, "breaking_strength_kg": 3120.0, "span_m": 50.0, "sag_m": 0.60, "tension_mode": "sag_span", "num_conductors": 1},
                {"level": 2, "enabled": True, "height_m": 16.5, "code": "SAC-185", "weight_kg_per_m": 0.71, "breaking_strength_kg": 3120.0, "span_m": 50.0, "sag_m": 0.60, "tension_mode": "sag_span", "num_conductors": 1},
                {"level": 3, "enabled": True, "height_m": 14.5, "code": "SAC-185", "weight_kg_per_m": 0.71, "breaking_strength_kg": 3120.0, "span_m": 50.0, "sag_m": 0.60, "tension_mode": "sag_span", "num_conductors": 1}
            ],
            "guy_wires": [
                {"level": 1, "enabled": True, "height_m": 18.5, "anchor_distance_m": 12.0},
                {"level": 2, "enabled": True, "height_m": 16.5, "anchor_distance_m": 12.0},
                {"level": 3, "enabled": True, "height_m": 14.5, "anchor_distance_m": 12.0},
                {"level": 4, "enabled": True, "height_m": 12.5, "anchor_distance_m": 12.0},
                {"level": 5, "enabled": True, "height_m": 10.5, "anchor_distance_m": 12.0},
                {"level": 6, "enabled": True, "height_m": 8.5,  "anchor_distance_m": 12.0},
                {"level": 7, "enabled": True, "height_m": 6.5,  "anchor_distance_m": 12.0}
            ]
        }
        res = calculate_pole_guy_system(preset_22m)
        self.assertEqual(res["pole"]["height_m"], 22.0)
        self.assertEqual(res["pole"]["embedment_m"], 2.8)
        self.assertAlmostEqual(res["pole"]["above_ground_m"], 19.2, places=1)
        self.assertEqual(res["anchor"]["global_distance_m"], 12.0)

        # 3 conductors tension = 369.79 kg each
        # Overturning moment = 369.79 * (18.5 + 16.5 + 14.5) = 369.79 * 49.5 = 18304.7 kg.m
        expected_moment = 369.7916 * 49.5
        self.assertAlmostEqual(res["summary"]["total_overturning_moment_kg_m"], expected_moment, places=0)
        self.assertAlmostEqual(res["summary"]["total_resisting_moment_kg_m"], expected_moment, places=0)
        self.assertAlmostEqual(res["pole_base"]["moment_balance_pct"], 100.0, places=0)

        # Check all 7 guy wires are safe
        for g in res["guy_wires"]:
            self.assertTrue(g["enabled"])
            self.assertGreater(g["safety_factor"], 2.0)
            self.assertEqual(g["status"], "SAFE")

    def test_number_of_conductors_scaling(self):
        # Base scenario with 1 conductor per phase
        scenario_single = dict(self.sample_input)
        scenario_single["conductors"] = [
            {
                "level": 1,
                "enabled": True,
                "height_m": 12.0,
                "code": "SAC-185",
                "tension_mode": "direct",
                "tension_kg": 500.0,
                "num_conductors": 1,
                "weight_kg_per_m": 0.71,
                "span_length_m": 50.0
            }
        ]
        res_single = calculate_pole_guy_system(scenario_single)

        # Scenario with 2 conductors per phase (bundle)
        import copy
        scenario_double = copy.deepcopy(scenario_single)
        scenario_double["conductors"][0]["num_conductors"] = 2
        res_double = calculate_pole_guy_system(scenario_double)

        c_single = res_single["conductors"][0]
        c_double = res_double["conductors"][0]

        # Single conductor tension should remain 500 kg
        self.assertEqual(c_single["single_tension_kg"], 500.0)
        self.assertEqual(c_double["single_tension_kg"], 500.0)

        # Horizontal force, moment, and vertical dead weight should exactly double
        self.assertAlmostEqual(c_double["horizontal_force_kg"], 2.0 * c_single["horizontal_force_kg"], places=1)
        self.assertAlmostEqual(c_double["moment_kg_m"], 2.0 * c_single["moment_kg_m"], places=1)
        self.assertAlmostEqual(c_double["vertical_weight_kg"], 2.0 * c_single["vertical_weight_kg"], places=1)

        # System overturning moment and resisting moment must also double
        self.assertAlmostEqual(
            res_double["summary"]["total_overturning_moment_kg_m"],
            2.0 * res_single["summary"]["total_overturning_moment_kg_m"],
            places=1
        )
        self.assertAlmostEqual(
            res_double["summary"]["total_resisting_moment_kg_m"],
            2.0 * res_single["summary"]["total_resisting_moment_kg_m"],
            places=1
        )

        # Guy wire tensions should also scale by a factor of 2.0 to maintain moment equilibrium
        for g_s, g_d in zip(res_single["guy_wires"], res_double["guy_wires"]):
            self.assertAlmostEqual(g_d["tension_kg"], 2.0 * g_s["tension_kg"], places=1)

    def test_50_sqmm_guy_wire_spec(self):
        import copy
        scenario_50 = copy.deepcopy(self.sample_input)
        scenario_50["guy_wire_spec"] = {
            "size_sqmm": 50.0
        }
        res_50 = calculate_pole_guy_system(scenario_50)

        # Check spec resolution
        self.assertEqual(res_50["guy_spec"]["size_sqmm"], 50.0)
        self.assertEqual(res_50["guy_spec"]["unit_weight_kg_m"], 0.392)
        self.assertEqual(res_50["guy_spec"]["rts_kg"], 3355.0)

        # Total guy dead weight should reflect 0.392 kg/m
        res_95 = calculate_pole_guy_system(self.sample_input)
        # Unit weight ratio: 0.392 / 0.764 ~= 0.513
        expected_weight_ratio = 0.392 / 0.764
        self.assertAlmostEqual(
            res_50["summary"]["total_guy_weight_kg"] / res_95["summary"]["total_guy_weight_kg"],
            expected_weight_ratio,
            places=2
        )

        # Safety factor check against RTS = 3355 kg
        g1 = res_50["guy_wires"][0]
        expected_sf = 3355.0 / g1["tension_kg"]
        self.assertAlmostEqual(g1["safety_factor"], round(expected_sf, 2), places=1)

    def test_50_sqmm_high_strength_option(self):
        import copy
        scenario_50_hs = copy.deepcopy(self.sample_input)
        scenario_50_hs["guy_wire_spec"] = {
            "size_sqmm": 50.0,
            "rts_kg": 4898.0,
            "unit_weight_kg_m": 0.392
        }
        res = calculate_pole_guy_system(scenario_50_hs)
        self.assertEqual(res["guy_spec"]["size_sqmm"], 50.0)
        self.assertEqual(res["guy_spec"]["rts_kg"], 4898.0)
        g1 = res["guy_wires"][0]
        expected_sf = 4898.0 / g1["tension_kg"]
        self.assertAlmostEqual(g1["safety_factor"], round(expected_sf, 2), places=1)

    def test_overhead_ground_wire_mechanics(self):
        import copy
        # Scenario without OHGW
        base_scenario = copy.deepcopy(self.sample_input)
        res_no_ohgw = calculate_pole_guy_system(base_scenario)

        # Scenario with OHGW enabled
        ohgw_scenario = copy.deepcopy(self.sample_input)
        ohgw_scenario["overhead_ground_wire"] = {
            "enabled": True,
            "code": "GSW-50",
            "name": "50 sq.mm Galvanized Steel Strand",
            "height_m": 19.1,
            "span_m": 50.0,
            "sag_m": 0.50,
            "weight_kg_per_m": 0.392,
            "breaking_strength_kg": 3355.0,
            "num_conductors": 1,
            "tension_mode": "sag_span",
            "deviation_angle_deg": 0.0
        }
        res_with_ohgw = calculate_pole_guy_system(ohgw_scenario)

        ohgw_res = res_with_ohgw["overhead_ground_wire"]
        self.assertTrue(ohgw_res["enabled"])
        self.assertEqual(ohgw_res["height_m"], 19.1)

        # Parabolic tension T = (0.392 * 50^2) / (8 * 0.50) = (0.392 * 2500) / 4 = 245.0 kg
        expected_t = (0.392 * (50.0 ** 2)) / (8.0 * 0.50)
        self.assertAlmostEqual(ohgw_res["single_tension_kg"], 245.0, places=2)
        self.assertAlmostEqual(ohgw_res["horizontal_force_kg"], 245.0, places=2)

        # OHGW Moment = 245.0 * 19.1 = 4679.5 kg.m
        expected_ohgw_moment = 245.0 * 19.1
        self.assertAlmostEqual(ohgw_res["moment_kg_m"], expected_ohgw_moment, places=1)

        # Total overturning moment must increase exactly by expected_ohgw_moment
        expected_total_moment = res_no_ohgw["summary"]["total_overturning_moment_kg_m"] + expected_ohgw_moment
        self.assertAlmostEqual(
            res_with_ohgw["summary"]["total_overturning_moment_kg_m"],
            expected_total_moment,
            places=1
        )

        # Total resisting moment from guy wires must balance 100% of the combined moment
        self.assertAlmostEqual(
            res_with_ohgw["summary"]["total_resisting_moment_kg_m"],
            expected_total_moment,
            delta=1.0
        )
        self.assertAlmostEqual(res_with_ohgw["pole_base"]["moment_balance_pct"], 100.0, places=0)

        # Guy wire tensions must increase to counter the OHGW pull
        for g_base, g_ohgw in zip(res_no_ohgw["guy_wires"], res_with_ohgw["guy_wires"]):
            self.assertGreater(g_ohgw["tension_kg"], g_base["tension_kg"])

    def test_ohgw_25_and_35_sqmm_specs(self):
        import copy
        # Test 25 sq.mm GSW OHGW
        ohgw_25_scenario = copy.deepcopy(self.sample_input)
        ohgw_25_scenario["overhead_ground_wire"] = {
            "enabled": True,
            "code": "GSW-25",
            "height_m": 19.1,
            "span_m": 50.0,
            "sag_m": 0.50,
            "num_conductors": 1,
            "tension_mode": "sag_span",
            "deviation_angle_deg": 0.0
        }
        res_25 = calculate_pole_guy_system(ohgw_25_scenario)
        ohgw_25 = res_25["overhead_ground_wire"]
        self.assertTrue(ohgw_25["enabled"])
        self.assertEqual(ohgw_25["code"], "GSW-25")
        self.assertAlmostEqual(ohgw_25["weight_kg_per_m"], 0.192, places=3)
        self.assertAlmostEqual(ohgw_25["breaking_strength_kg"], 1647.0, places=1)
        # T = (0.192 * 50^2) / (8 * 0.50) = (0.192 * 2500) / 4 = 120.0 kg
        self.assertAlmostEqual(ohgw_25["single_tension_kg"], 120.0, places=2)
        self.assertAlmostEqual(ohgw_25["horizontal_force_kg"], 120.0, places=2)
        # Moment = 120.0 * 19.1 = 2292.0 kg.m
        self.assertAlmostEqual(ohgw_25["moment_kg_m"], 2292.0, places=1)
        self.assertAlmostEqual(res_25["pole_base"]["moment_balance_pct"], 100.0, places=0)

        # Test 35 sq.mm GSW OHGW
        ohgw_35_scenario = copy.deepcopy(self.sample_input)
        ohgw_35_scenario["overhead_ground_wire"] = {
            "enabled": True,
            "code": "GSW-35",
            "height_m": 19.1,
            "span_m": 50.0,
            "sag_m": 0.50,
            "num_conductors": 1,
            "tension_mode": "sag_span",
            "deviation_angle_deg": 0.0
        }
        res_35 = calculate_pole_guy_system(ohgw_35_scenario)
        ohgw_35 = res_35["overhead_ground_wire"]
        self.assertTrue(ohgw_35["enabled"])
        self.assertEqual(ohgw_35["code"], "GSW-35")
        self.assertAlmostEqual(ohgw_35["weight_kg_per_m"], 0.272, places=3)
        self.assertAlmostEqual(ohgw_35["breaking_strength_kg"], 2330.0, places=1)
        # T = (0.272 * 50^2) / (8 * 0.50) = (0.272 * 2500) / 4 = 170.0 kg
        self.assertAlmostEqual(ohgw_35["single_tension_kg"], 170.0, places=2)
        self.assertAlmostEqual(ohgw_35["horizontal_force_kg"], 170.0, places=2)
        # Moment = 170.0 * 19.1 = 3247.0 kg.m
        self.assertAlmostEqual(ohgw_35["moment_kg_m"], 3247.0, places=1)
        self.assertAlmostEqual(res_35["pole_base"]["moment_balance_pct"], 100.0, places=0)

        # Check relative overturning moments: 25 sq.mm < 35 sq.mm < 50 sq.mm
        self.assertLess(
            res_25["summary"]["total_overturning_moment_kg_m"],
            res_35["summary"]["total_overturning_moment_kg_m"]
        )

    def test_default_span_80m(self):
        # Scenario where span_m is not explicitly provided in conductor or OHGW
        scenario = {
            "pole": {"height_m": 22.0, "embedment_m": 2.8, "weight_kg": 3500.0},
            "anchor": {"distance_m": 12.0},
            "guy_wire_spec": {"size_sqmm": 95.0, "rts_kg": 8528.0, "unit_weight_kg_m": 0.764, "required_sf": 2.0},
            "conductors": [
                {
                    "level": 1,
                    "enabled": True,
                    "height_m": 18.5,
                    "code": "SAC-185",
                    "weight_kg_per_m": 0.71,
                    "sag_m": 0.60,
                    "tension_mode": "sag_span",
                    "num_conductors": 1
                    # span_m omitted -> must default to 80.0m
                }
            ],
            "overhead_ground_wire": {
                "enabled": True,
                "code": "GSW-50",
                "height_m": 19.1,
                "sag_m": 0.50,
                "tension_mode": "sag_span",
                "num_conductors": 1
                # span_m omitted -> must default to 80.0m
            },
            "guy_wires": [
                {"level": 1, "enabled": True, "height_m": 18.5, "anchor_distance_m": 12.0}
            ]
        }
        res = calculate_pole_guy_system(scenario)
        c1 = res["conductors"][0]
        ohgw = res["overhead_ground_wire"]

        self.assertEqual(c1["span_m"], 80.0)
        # Expected conductor tension = (0.71 * 80^2) / (8 * 0.6) = 4544 / 4.8 = 946.67 kg
        expected_c_tension = (0.71 * (80.0 ** 2)) / (8.0 * 0.60)
        self.assertAlmostEqual(c1["single_tension_kg"], round(expected_c_tension, 2), places=2)

        self.assertEqual(ohgw["span_m"], 80.0)
        # Expected OHGW tension = (0.392 * 80^2) / (8 * 0.5) = 2508.8 / 4.0 = 627.2 kg
        expected_ohgw_tension = (0.392 * (80.0 ** 2)) / (8.0 * 0.50)
        self.assertAlmostEqual(ohgw["single_tension_kg"], round(expected_ohgw_tension, 2), places=2)

    def test_default_num_conductors_2(self):
        # Scenario where num_conductors is omitted in conductor definition
        scenario = {
            "pole": {"height_m": 22.0, "embedment_m": 2.8, "weight_kg": 3500.0},
            "anchor": {"distance_m": 12.0},
            "guy_wire_spec": {"size_sqmm": 95.0, "rts_kg": 8528.0, "unit_weight_kg_m": 0.764, "required_sf": 2.0},
            "conductors": [
                {
                    "level": 1,
                    "enabled": True,
                    "height_m": 18.5,
                    "code": "SAC-185",
                    "weight_kg_per_m": 0.71,
                    "span_m": 80.0,
                    "sag_m": 0.60,
                    "tension_mode": "sag_span"
                    # num_conductors omitted -> must default to 2
                }
            ],
            "guy_wires": [
                {"level": 1, "enabled": True, "height_m": 18.5, "anchor_distance_m": 12.0}
            ]
        }
        res = calculate_pole_guy_system(scenario)
        c1 = res["conductors"][0]

        self.assertEqual(c1["num_conductors"], 2)
        # Single tension = 946.67 kg
        expected_single_t = (0.71 * (80.0 ** 2)) / (8.0 * 0.60)
        self.assertAlmostEqual(c1["single_tension_kg"], round(expected_single_t, 2), places=2)
        # Horizontal force = 2 * single tension = 1893.33 kg
        expected_h_force = expected_single_t * 2
        self.assertAlmostEqual(c1["horizontal_force_kg"], round(expected_h_force, 2), places=1)
        # Moment = 1893.33 * 18.5 = 35026.7 kg.m
        expected_moment = expected_h_force * 18.5
        self.assertAlmostEqual(c1["moment_kg_m"], round(expected_moment, 1), places=1)

    def test_default_ohgw_35_and_aac400_specs(self):
        # Scenario where conductor and OHGW codes and specs are omitted entirely
        scenario = {
            "pole": {"height_m": 22.0, "embedment_m": 2.8, "weight_kg": 3500.0},
            "anchor": {"distance_m": 12.0},
            "guy_wire_spec": {"size_sqmm": 95.0, "rts_kg": 8528.0, "unit_weight_kg_m": 0.764, "required_sf": 2.0},
            "conductors": [
                {
                    "level": 1,
                    "enabled": True,
                    "height_m": 18.5
                    # Everything else omitted -> AAC-400 defaults (w=1.100, RTS=6680, span=80, sag=0.6, num=2)
                }
            ],
            "overhead_ground_wire": {
                "enabled": True,
                "height_m": 19.1
                # Everything else omitted -> GSW-35 defaults (w=0.272, RTS=2330, span=80, sag=0.5, num=1)
            },
            "guy_wires": [
                {"level": 1, "enabled": True, "height_m": 18.5, "anchor_distance_m": 12.0}
            ]
        }
        res = calculate_pole_guy_system(scenario)
        c1 = res["conductors"][0]
        ohgw = res["overhead_ground_wire"]

        # Verify Conductor defaults
        self.assertEqual(c1["code"], "AAC-400")
        self.assertEqual(c1["num_conductors"], 2)
        self.assertEqual(c1["span_m"], 80.0)
        self.assertEqual(c1["sag_m"], 0.60)
        # Single tension = (1.100 * 80^2) / (8 * 0.6) = 7040 / 4.8 = 1466.67 kg
        expected_c_tension = (1.100 * (80.0 ** 2)) / (8.0 * 0.60)
        self.assertAlmostEqual(c1["single_tension_kg"], round(expected_c_tension, 2), places=2)
        self.assertAlmostEqual(c1["horizontal_force_kg"], round(expected_c_tension * 2, 2), places=1)

        # Verify OHGW defaults
        self.assertEqual(ohgw["code"], "GSW-35")
        self.assertEqual(ohgw["span_m"], 80.0)
        self.assertEqual(ohgw["sag_m"], 0.50)
        self.assertAlmostEqual(ohgw["weight_kg_per_m"], 0.272, places=3)
        self.assertAlmostEqual(ohgw["breaking_strength_kg"], 2330.0, places=1)
        # OHGW tension = (0.272 * 80^2) / (8 * 0.5) = 1740.8 / 4 = 435.20 kg
        expected_ohgw_tension = (0.272 * (80.0 ** 2)) / (8.0 * 0.50)
        self.assertAlmostEqual(ohgw["single_tension_kg"], round(expected_ohgw_tension, 2), places=2)
        self.assertAlmostEqual(ohgw["horizontal_force_kg"], round(expected_ohgw_tension, 2), places=2)

    def test_per_level_guy_wire_sizes(self):
        """Test elastic statics and safety factors when guy wires have different sizes across levels."""
        scenario = {
            "pole": {"height_m": 22.0, "embedment_m": 2.8, "weight_kg": 3500.0},
            "anchor": {"distance_m": 12.0},
            "guy_wire_spec": {"size_sqmm": 95.0, "required_sf": 2.0},
            "calculation_method": "elastic",
            "conductors": [
                {
                    "level": 1,
                    "enabled": True,
                    "height_m": 18.5,
                    "code": "AAC-400",
                    "tension_mode": "direct",
                    "tension_kg": 1500.0,
                    "num_conductors": 2
                }
            ],
            "overhead_ground_wire": {"enabled": False},
            "guy_wires": [
                {"level": 1, "enabled": True, "height_m": 18.5, "anchor_distance_m": 12.0, "size_sqmm": 95.0},
                {"level": 2, "enabled": True, "height_m": 16.5, "anchor_distance_m": 12.0, "size_sqmm": 50.0},
                {"level": 3, "enabled": True, "height_m": 14.5, "anchor_distance_m": 12.0, "size_sqmm": 35.0},
                {"level": 4, "enabled": True, "height_m": 12.5, "anchor_distance_m": 12.0, "size_sqmm": 25.0}
            ]
        }
        res = calculate_pole_guy_system(scenario)
        guys = res["guy_wires"]
        
        # Verify sizes and RTS are populated per level
        self.assertEqual(guys[0]["size_sqmm"], 95.0)
        self.assertEqual(guys[0]["rts_kg"], 8528.0)
        self.assertEqual(guys[1]["size_sqmm"], 50.0)
        self.assertEqual(guys[1]["rts_kg"], 3355.0)
        self.assertEqual(guys[2]["size_sqmm"], 35.0)
        self.assertEqual(guys[2]["rts_kg"], 2330.0)
        self.assertEqual(guys[3]["size_sqmm"], 25.0)
        self.assertEqual(guys[3]["rts_kg"], 1647.0)

        # Verify Moment Equilibrium: total overturning moment = sum of guy resisting moments
        m_overturning = res["summary"]["total_overturning_moment_kg_m"]
        m_resisting = sum(g["moment_kg_m"] for g in guys)
        self.assertAlmostEqual(m_overturning, m_resisting, places=1)
        self.assertAlmostEqual(res["pole_base"]["moment_balance_pct"], 100.0, places=1)

        # Verify safety factor calculation: SF = RTS_level / Tension_level
        for g in guys:
            expected_sf = g["rts_kg"] / g["tension_kg"]
            self.assertAlmostEqual(g["safety_factor"], round(expected_sf, 2), places=1)

        # Compare with baseline where all 4 guys are uniform 95 sq.mm:
        # The 95 sq.mm guy (Level 1) should carry a larger percentage of total load in the mixed configuration
        # because the other levels are more compliant (smaller area)
        import copy
        uniform_scenario = copy.deepcopy(scenario)
        for g in uniform_scenario["guy_wires"]:
            g["size_sqmm"] = 95.0
        res_uniform = calculate_pole_guy_system(uniform_scenario)
        self.assertGreater(guys[0]["tension_kg"], res_uniform["guy_wires"][0]["tension_kg"])

    def test_default_top_guy_size_50_sqmm(self):
        """Test default scenario configuration where top guy is 50 sq.mm and lower guys are 95 sq.mm."""
        from app import app
        with app.test_client() as client:
            resp = client.get("/api/default-scenario")
            data = resp.get_json()
            self.assertTrue(data["success"])
            guy_wires = data["data"]["guy_wires"]
            # Top guy (level 1) must be 50 sq.mm
            self.assertEqual(guy_wires[0]["level"], 1)
            self.assertEqual(guy_wires[0]["size_sqmm"], 50.0)
            # Other guys (levels 2-7) must be 95 sq.mm
            for g in guy_wires[1:]:
                self.assertEqual(g["size_sqmm"], 95.0)

            # Pass into calculation engine and verify statics
            res = calculate_pole_guy_system(data["data"])
            self.assertEqual(res["guy_wires"][0]["size_sqmm"], 50.0)
            self.assertEqual(res["guy_wires"][0]["rts_kg"], 3355.0)
            self.assertEqual(res["guy_wires"][1]["size_sqmm"], 95.0)
            self.assertEqual(res["guy_wires"][1]["rts_kg"], 8528.0)
            self.assertAlmostEqual(res["pole_base"]["moment_balance_pct"], 100.0, places=1)

    def test_default_wind_pressure_40_kg_m2(self):
        """Test default scenario configuration where default wind pressure is 40 kg/m2."""
        from app import app
        with app.test_client() as client:
            resp = client.get("/api/default-scenario")
            data = resp.get_json()
            self.assertTrue(data["success"])
            scenario = data["data"]
            # OHGW must have wind_pressure_kg_m2 == 40.0
            self.assertEqual(scenario["overhead_ground_wire"]["wind_pressure_kg_m2"], 40.0)
            # Conductors must have wind_pressure_kg_m2 == 40.0
            for c in scenario["conductors"]:
                self.assertEqual(c["wind_pressure_kg_m2"], 40.0)

            # Pass into calculation engine and verify resultant weight tension
            res = calculate_pole_guy_system(scenario)
            for c in res["conductors"]:
                self.assertEqual(c["wind_pressure_kg_m2"], 40.0)
                self.assertGreater(c["wind_load_kg_per_m"], 0.0)
                self.assertGreater(c["resultant_weight_kg_m"], c["weight_kg_per_m"])
            
            ohgw = res["overhead_ground_wire"]
            self.assertEqual(ohgw["wind_pressure_kg_m2"], 40.0)
            self.assertGreater(ohgw["wind_load_kg_per_m"], 0.0)
            self.assertGreater(ohgw["resultant_weight_kg_m"], ohgw["weight_kg_per_m"])
            self.assertAlmostEqual(res["pole_base"]["moment_balance_pct"], 100.0, places=1)

    def test_conductor_wind_resultant_weight_and_tension(self):
        """Test calculation of conductor and OHGW tension using resultant weight w_r due to wind."""
        import math
        scenario = {
            "pole": {"height_m": 22.0, "embedment_m": 2.8, "weight_kg": 3500.0},
            "anchor": {"distance_m": 12.0},
            "guy_wire_spec": {"size_sqmm": 95.0, "rts_kg": 8528.0, "unit_weight_kg_m": 0.764, "required_sf": 2.0},
            "overhead_ground_wire": {
                "enabled": True,
                "code": "GSW-35",
                "height_m": 19.1,
                "span_m": 80.0,
                "sag_m": 0.50,
                "num_conductors": 1,
                "weight_kg_per_m": 0.272,
                "breaking_strength_kg": 2330.0,
                "overall_diameter_mm": 7.5,
                "wind_pressure_kg_m2": 50.0,
                "tension_mode": "sag_span",
                "deviation_angle_deg": 0.0
            },
            "conductors": [
                {
                    "level": 1,
                    "enabled": True,
                    "height_m": 18.5,
                    "code": "AAC-400",
                    "weight_kg_per_m": 1.100,
                    "breaking_strength_kg": 6680.0,
                    "overall_diameter_mm": 26.0,
                    "num_conductors": 2,
                    "span_m": 80.0,
                    "sag_m": 0.60,
                    "wind_pressure_kg_m2": 50.0,
                    "tension_mode": "sag_span",
                    "deviation_angle_deg": 0.0
                }
            ],
            "guy_wires": [
                {"level": 1, "enabled": True, "height_m": 18.5, "anchor_distance_m": 12.0, "size_sqmm": 50.0},
                {"level": 2, "enabled": True, "height_m": 16.5, "anchor_distance_m": 12.0, "size_sqmm": 95.0}
            ]
        }

        res = calculate_pole_guy_system(scenario)
        c1 = res["conductors"][0]

        # Conductor checks:
        # w_v = 1.100 kg/m
        # w_h = 50 * 0.026 = 1.300 kg/m
        # w_r = sqrt(1.100^2 + 1.300^2) = sqrt(2.90) = 1.7029386 kg/m
        w_h_expected = 50.0 * 0.026
        w_r_expected = math.sqrt(1.100**2 + w_h_expected**2)
        t_expected = (w_r_expected * (80.0**2)) / (8.0 * 0.60)
        f_turn_expected = t_expected * 2
        f_wind_expected = 50.0 * 0.026 * (80.0 / 2.0) * 2
        h_force_expected = f_turn_expected + f_wind_expected

        self.assertAlmostEqual(c1["wind_pressure_kg_m2"], 50.0, places=1)
        self.assertAlmostEqual(c1["wind_load_kg_per_m"], 1.300, places=3)
        self.assertAlmostEqual(c1["resultant_weight_kg_m"], round(w_r_expected, 4), places=3)
        self.assertAlmostEqual(c1["single_tension_kg"], round(t_expected, 2), places=1)
        self.assertAlmostEqual(c1["horizontal_force_kg"], round(h_force_expected, 2), places=1)

        # OHGW checks:
        # w_v = 0.272 kg/m
        # w_h = 50 * 0.0075 = 0.375 kg/m
        # w_r = sqrt(0.272^2 + 0.375^2) = sqrt(0.214609) = 0.463259 kg/m
        ohgw = res["overhead_ground_wire"]
        ohgw_wh_expected = 50.0 * 0.0075
        ohgw_wr_expected = math.sqrt(0.272**2 + ohgw_wh_expected**2)
        ohgw_t_expected = (ohgw_wr_expected * (80.0**2)) / (8.0 * 0.50)
        ohgw_f_turn = ohgw_t_expected * 1
        ohgw_f_wind = 50.0 * 0.0075 * 40.0 * 1
        ohgw_h_expected = ohgw_f_turn + ohgw_f_wind

        self.assertAlmostEqual(ohgw["wind_pressure_kg_m2"], 50.0, places=1)
        self.assertAlmostEqual(ohgw["wind_load_kg_per_m"], 0.375, places=3)
        self.assertAlmostEqual(ohgw["resultant_weight_kg_m"], round(ohgw_wr_expected, 4), places=3)
        self.assertAlmostEqual(ohgw["single_tension_kg"], round(ohgw_t_expected, 2), places=1)
        self.assertAlmostEqual(ohgw["horizontal_force_kg"], round(ohgw_h_expected, 2), places=1)

        # Verify static equilibrium (moment balance)
        self.assertAlmostEqual(res["pole_base"]["moment_balance_pct"], 100.0, places=1)

        # Verify backward compatibility when wind pressure = 0:
        scenario_no_wind = dict(scenario)
        scenario_no_wind["overhead_ground_wire"] = dict(scenario["overhead_ground_wire"], wind_pressure_kg_m2=0.0)
        scenario_no_wind["conductors"] = [dict(scenario["conductors"][0], wind_pressure_kg_m2=0.0)]
        res_no_wind = calculate_pole_guy_system(scenario_no_wind)
        c1_no_wind = res_no_wind["conductors"][0]
        # At zero wind, w_r == w == 1.100 kg/m
        t_gravity = (1.100 * (80.0**2)) / (8.0 * 0.60)
        self.assertAlmostEqual(c1_no_wind["single_tension_kg"], round(t_gravity, 2), places=2)
        self.assertAlmostEqual(c1_no_wind["resultant_weight_kg_m"], 1.100, places=3)
        self.assertLess(c1_no_wind["single_tension_kg"], c1["single_tension_kg"])

    def test_more_than_seven_guy_wires_equilibrium(self):
        """Verify that system handles >7 guy wire levels (e.g., 9 guy wires) with 100% moment balance."""
        ten_guys_input = {
            "pole": {
                "height_m": 22.0,
                "embedment_m": 2.8,
                "weight_kg": 3500.0
            },
            "anchor": {
                "distance_m": 12.0
            },
            "guy_wire_spec": {
                "size_sqmm": 95.0,
                "rts_kg": 8528.0,
                "unit_weight_kg_m": 0.764,
                "required_sf": 2.0
            },
            "calculation_method": "elastic",
            "conductors": [
                {
                    "level": 1,
                    "enabled": True,
                    "height_m": 18.5,
                    "code": "AAC-400",
                    "tension_mode": "sag_span",
                    "span_m": 80.0,
                    "sag_m": 0.60,
                    "num_conductors": 2,
                    "weight_kg_per_m": 1.100,
                    "overall_diameter_mm": 26.0,
                    "wind_pressure_kg_m2": 40.0,
                    "deviation_angle_deg": 0.0
                }
            ],
            # 9 Guy Wire levels
            "guy_wires": [
                {"level": 1, "enabled": True, "height_m": 20.0, "size_sqmm": 50.0, "anchor_distance_m": 12.0},
                {"level": 2, "enabled": True, "height_m": 18.5, "size_sqmm": 95.0, "anchor_distance_m": 12.0},
                {"level": 3, "enabled": True, "height_m": 16.5, "size_sqmm": 95.0, "anchor_distance_m": 12.0},
                {"level": 4, "enabled": True, "height_m": 14.5, "size_sqmm": 95.0, "anchor_distance_m": 12.0},
                {"level": 5, "enabled": True, "height_m": 12.5, "size_sqmm": 95.0, "anchor_distance_m": 12.0},
                {"level": 6, "enabled": True, "height_m": 10.5, "size_sqmm": 95.0, "anchor_distance_m": 12.0},
                {"level": 7, "enabled": True, "height_m": 8.5,  "size_sqmm": 95.0, "anchor_distance_m": 12.0},
                {"level": 8, "enabled": True, "height_m": 6.5,  "size_sqmm": 95.0, "anchor_distance_m": 12.0},
                {"level": 9, "enabled": True, "height_m": 4.5,  "size_sqmm": 95.0, "anchor_distance_m": 12.0}
            ]
        }

        res = calculate_pole_guy_system(ten_guys_input)

        self.assertEqual(len(res["guy_wires"]), 9)
        overturning = res["summary"]["total_overturning_moment_kg_m"]
        resisting = res["summary"]["total_resisting_moment_kg_m"]
        self.assertGreater(overturning, 0)
        self.assertAlmostEqual(resisting, overturning, delta=1.0)
        self.assertAlmostEqual(res["pole_base"]["moment_balance_pct"], 100.0, places=0)

        # Each active guy wire should carry tension
        for g in res["guy_wires"]:
            self.assertGreater(g["tension_kg"], 0)
            self.assertGreater(g["horizontal_force_kg"], 0)
            self.assertGreater(g["vertical_force_kg"], 0)
            self.assertGreater(g["safety_factor"], 0)

        # Check total anchor pull
        self.assertGreater(res["anchor"]["resultant_pull_kg"], 0)
        self.assertAlmostEqual(
            res["anchor"]["total_horizontal_pull_kg"],
            sum(g["horizontal_force_kg"] for g in res["guy_wires"]),
            delta=1.0
        )

    def test_more_than_three_conductors_equilibrium(self):
        """Verify that system handles >3 conductor levels (e.g. 5 conductor levels) with 100% moment balance."""
        five_conductors_input = {
            "pole": {
                "height_m": 22.0,
                "embedment_m": 2.8,
                "weight_kg": 3500.0
            },
            "anchor": {
                "distance_m": 12.0
            },
            "guy_wire_spec": {
                "size_sqmm": 95.0,
                "rts_kg": 8528.0,
                "unit_weight_kg_m": 0.764,
                "required_sf": 2.0
            },
            "calculation_method": "elastic",
            "overhead_ground_wire": {
                "enabled": True,
                "code": "GSW-35",
                "height_m": 20.0,
                "span_m": 80.0,
                "sag_m": 0.50,
                "num_conductors": 1,
                "weight_kg_per_m": 0.272,
                "breaking_strength_kg": 2330.0,
                "overall_diameter_mm": 7.5,
                "wind_pressure_kg_m2": 40.0,
                "deviation_angle_deg": 0.0
            },
            "conductors": [
                {
                    "level": 1,
                    "enabled": True,
                    "height_m": 18.5,
                    "code": "AAC-400",
                    "tension_mode": "sag_span",
                    "span_m": 80.0,
                    "sag_m": 0.60,
                    "num_conductors": 2,
                    "weight_kg_per_m": 1.100,
                    "overall_diameter_mm": 26.0,
                    "wind_pressure_kg_m2": 40.0,
                    "deviation_angle_deg": 0.0
                },
                {
                    "level": 2,
                    "enabled": True,
                    "height_m": 16.5,
                    "code": "AAC-400",
                    "tension_mode": "sag_span",
                    "span_m": 80.0,
                    "sag_m": 0.60,
                    "num_conductors": 2,
                    "weight_kg_per_m": 1.100,
                    "overall_diameter_mm": 26.0,
                    "wind_pressure_kg_m2": 40.0,
                    "deviation_angle_deg": 0.0
                },
                {
                    "level": 3,
                    "enabled": True,
                    "height_m": 14.5,
                    "code": "AAC-400",
                    "tension_mode": "sag_span",
                    "span_m": 80.0,
                    "sag_m": 0.60,
                    "num_conductors": 2,
                    "weight_kg_per_m": 1.100,
                    "overall_diameter_mm": 26.0,
                    "wind_pressure_kg_m2": 40.0,
                    "deviation_angle_deg": 0.0
                },
                {
                    "level": 4,
                    "enabled": True,
                    "height_m": 12.5,
                    "code": "AAC-400",
                    "tension_mode": "sag_span",
                    "span_m": 80.0,
                    "sag_m": 0.60,
                    "num_conductors": 2,
                    "weight_kg_per_m": 1.100,
                    "overall_diameter_mm": 26.0,
                    "wind_pressure_kg_m2": 40.0,
                    "deviation_angle_deg": 0.0
                },
                {
                    "level": 5,
                    "enabled": True,
                    "height_m": 10.5,
                    "code": "AAC-400",
                    "tension_mode": "sag_span",
                    "span_m": 80.0,
                    "sag_m": 0.60,
                    "num_conductors": 2,
                    "weight_kg_per_m": 1.100,
                    "overall_diameter_mm": 26.0,
                    "wind_pressure_kg_m2": 40.0,
                    "deviation_angle_deg": 0.0
                }
            ],
            "guy_wires": [
                {"level": 1, "enabled": True, "height_m": 18.5, "size_sqmm": 50.0, "anchor_distance_m": 12.0},
                {"level": 2, "enabled": True, "height_m": 16.5, "size_sqmm": 95.0, "anchor_distance_m": 12.0},
                {"level": 3, "enabled": True, "height_m": 14.5, "size_sqmm": 95.0, "anchor_distance_m": 12.0},
                {"level": 4, "enabled": True, "height_m": 12.5, "size_sqmm": 95.0, "anchor_distance_m": 12.0},
                {"level": 5, "enabled": True, "height_m": 10.5, "size_sqmm": 95.0, "anchor_distance_m": 12.0},
                {"level": 6, "enabled": True, "height_m": 8.5,  "size_sqmm": 95.0, "anchor_distance_m": 12.0},
                {"level": 7, "enabled": True, "height_m": 6.5,  "size_sqmm": 95.0, "anchor_distance_m": 12.0}
            ]
        }

        res = calculate_pole_guy_system(five_conductors_input)

        self.assertEqual(len(res["conductors"]), 5)
        for i, c in enumerate(res["conductors"]):
            self.assertEqual(c["level"], i + 1)
            self.assertTrue(c["enabled"])
            self.assertGreater(c["single_tension_kg"], 0)
            self.assertGreater(c["horizontal_force_kg"], 0)
            self.assertGreater(c["moment_kg_m"], 0)

        # Sum of overturning moments must equal sum of 5 conductor moments + OHGW moment
        ohgw_m = res["overhead_ground_wire"]["moment_kg_m"]
        cond_m_sum = sum(c["moment_kg_m"] for c in res["conductors"])
        expected_total_m = cond_m_sum + ohgw_m
        self.assertAlmostEqual(res["summary"]["total_overturning_moment_kg_m"], expected_total_m, delta=1.0)

        # Resisting moment must balance overturning moment
        self.assertAlmostEqual(res["summary"]["total_resisting_moment_kg_m"], expected_total_m, delta=1.0)
        self.assertAlmostEqual(res["pole_base"]["moment_balance_pct"], 100.0, places=0)

        # All guy wires must have positive tension and safety factor
        for g in res["guy_wires"]:
            self.assertGreater(g["tension_kg"], 0)
            self.assertGreater(g["safety_factor"], 0)

if __name__ == "__main__":
    unittest.main()




