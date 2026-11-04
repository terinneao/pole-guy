"""
Engineering Statics and Mechanics Calculation Engine for Pole Guy Wires.
Units: kg (force/mass), meter (length), degrees / radians (angle).
"""

import math
from typing import Dict, List, Any, Optional

STANDARD_GUY_SPECS = {
    25: {
        "size_sqmm": 25.0,
        "name": "25 sq.mm Galvanized Steel Strand",
        "standard": "PEA / TIS 404 / ASTM A475 (7/2.10 mm)",
        "unit_weight_kg_m": 0.192,
        "default_rts_kg": 1647.0,  # 16.15 kN
        "rts_options": [
            {"label": "Standard / Utility Grade (1,647 kg / 16.15 kN)", "value": 1647.0}
        ]
    },
    35: {
        "size_sqmm": 35.0,
        "name": "35 sq.mm Galvanized Steel Strand",
        "standard": "PEA / TIS 404 / ASTM A475 (7/2.50 mm)",
        "unit_weight_kg_m": 0.272,
        "default_rts_kg": 2330.0,  # 22.85 kN
        "rts_options": [
            {"label": "Standard / Utility Grade (2,330 kg / 22.85 kN)", "value": 2330.0}
        ]
    },
    50: {
        "size_sqmm": 50.0,
        "name": "50 sq.mm Galvanized Steel Strand",
        "standard": "PEA / TIS 404 / ASTM A475 (7/3.00 mm)",
        "unit_weight_kg_m": 0.392,
        "default_rts_kg": 3355.0,  # 32.9 kN (PEA Utility Grade)
        "rts_options": [
            {"label": "Standard / Utility Grade (3,355 kg / 32.9 kN)", "value": 3355.0},
            {"label": "High Strength HS (4,898 kg / 48.0 kN)", "value": 4898.0},
            {"label": "Extra High Strength EHS (6,985 kg / 68.5 kN)", "value": 6985.0}
        ]
    },
    95: {
        "size_sqmm": 95.0,
        "name": "95 sq.mm Galvanized Steel Strand",
        "standard": "PEA / TIS 404 / ASTM A475 (7/4.15 mm)",
        "unit_weight_kg_m": 0.764,
        "default_rts_kg": 8528.0,  # 83.6 kN (High Strength Grade)
        "rts_options": [
            {"label": "High Strength HS (8,528 kg / 83.6 kN)", "value": 8528.0},
            {"label": "Extra High Strength EHS (11,600 kg / 113.8 kN)", "value": 11600.0}
        ]
    }
}

STANDARD_OHGW_SPECS = {
    "GSW-25": {
        "code": "GSW-25",
        "name": "25 sq.mm Galvanized Steel Strand",
        "size_sqmm": 25.0,
        "strand": "7/2.10 mm",
        "diameter_mm": 6.30,
        "weight_kg_per_m": 0.192,
        "breaking_strength_kg": 1647.0,  # 16.15 kN (PEA / TIS 404)
        "standard": "PEA / TIS 404"
    },
    "GSW-35": {
        "code": "GSW-35",
        "name": "35 sq.mm Galvanized Steel Strand",
        "size_sqmm": 35.0,
        "strand": "7/2.50 mm",
        "diameter_mm": 7.50,
        "weight_kg_per_m": 0.272,
        "breaking_strength_kg": 2330.0,  # 22.85 kN (PEA / TIS 404)
        "standard": "PEA / TIS 404"
    },
    "GSW-50": {
        "code": "GSW-50",
        "name": "50 sq.mm Galvanized Steel Strand",
        "size_sqmm": 50.0,
        "strand": "7/3.00 mm",
        "diameter_mm": 9.00,
        "weight_kg_per_m": 0.392,
        "breaking_strength_kg": 3355.0,  # 32.90 kN (PEA / TIS 404)
        "standard": "PEA / TIS 404"
    },
    "GSW-95": {
        "code": "GSW-95",
        "name": "95 sq.mm Galvanized Steel Strand",
        "size_sqmm": 95.0,
        "strand": "7/4.15 mm",
        "diameter_mm": 12.50,
        "weight_kg_per_m": 0.764,
        "breaking_strength_kg": 8528.0,  # 83.60 kN (PEA / TIS 404)
        "standard": "PEA / TIS 404"
    },
    "ACSR-50": {
        "code": "ACSR-50",
        "name": "ACSR 50 sq.mm",
        "size_sqmm": 50.0,
        "strand": "6/3.20 + 1/3.20 mm",
        "diameter_mm": 9.60,
        "weight_kg_per_m": 0.187,
        "breaking_strength_kg": 1480.0,
        "standard": "PEA / IEC"
    }
}

def calculate_pole_guy_system(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform complete statics and structural check of the pole guy wire system.
    
    Inputs:
    - pole: { height_m, embedment_m, weight_kg }
    - anchor: { distance_m }
    - guy_wire_spec: { size_sqmm, rts_kg, unit_weight_kg_m, required_sf }
    - calculation_method: 'elastic' | 'equal_moment' | 'equal_shear'
    - conductors: list of up to 3 conductor levels:
        { id, level, enabled, height_m, code, name, breaking_strength_kg,
          unit_weight_kg_m, overall_diameter_mm, tension_mode, tension_kg,
          tension_ratio, num_conductors, span_length_m, wind_pressure_kg_m2,
          deviation_angle_deg }
    - guy_wires: list of up to 7 guy wire levels:
        { level, enabled, height_m, anchor_distance_m }
    """
    pole = input_data.get("pole", {})
    pole_height = float(pole.get("height_m", 14.3))
    pole_embedment = float(pole.get("embedment_m", 2.0))
    pole_weight = float(pole.get("weight_kg", 1200.0))
    pole_above_ground = max(0.0, pole_height - pole_embedment)

    global_anchor_dist = float(input_data.get("anchor", {}).get("distance_m", 8.0))
    
    guy_spec = input_data.get("guy_wire_spec", {})
    raw_size = float(guy_spec.get("size_sqmm", 95.0))
    closest_size = min(STANDARD_GUY_SPECS.keys(), key=lambda s: abs(s - raw_size))
    spec_info = STANDARD_GUY_SPECS.get(closest_size, STANDARD_GUY_SPECS[95])

    guy_type = guy_spec.get("name") or guy_spec.get("type") or spec_info["name"]
    guy_size = float(guy_spec.get("size_sqmm", spec_info["size_sqmm"]))
    guy_rts = float(guy_spec.get("rts_kg", spec_info["default_rts_kg"]))
    guy_unit_wt = float(guy_spec.get("unit_weight_kg_m", spec_info["unit_weight_kg_m"])) # kg/m
    required_sf = float(guy_spec.get("required_sf", 2.0))
    
    calc_method = input_data.get("calculation_method", "elastic")
    
    # Process Conductor Levels
    raw_conductors = input_data.get("conductors", [])
    conductor_results = []
    total_conductor_h_force = 0.0
    total_overturning_moment = 0.0
    total_conductor_weight = 0.0

    for idx, c in enumerate(raw_conductors):
        level_num = c.get("level", idx + 1)
        enabled = bool(c.get("enabled", True))
        height_m = float(c.get("height_m", 12.0 - idx * 1.5))
        num_cond = max(1, int(c.get("num_conductors", 2)))
        rts_kg = float(c.get("breaking_strength_kg", 6680.0))
        unit_wt = float(c.get("weight_kg_per_m", 1.100))
        diam_mm = float(c.get("overall_diameter_mm", 26.0))
        span_m = max(1.0, float(c.get("span_m", c.get("span_length_m", 80.0))))
        sag_m = max(0.01, float(c.get("sag_m", 0.60)))
        wind_p = max(0.0, float(c.get("wind_pressure_kg_m2", 0.0)))
        angle_deg = float(c.get("deviation_angle_deg", 0.0))
        
        mode = c.get("tension_mode", "sag_span")

        # Wind load per meter on single conductor: w_wind = P_wind * (diam_mm / 1000)
        w_wind = wind_p * (diam_mm / 1000.0)
        # Resultant unit weight per meter: w_r = sqrt(w^2 + w_wind^2)
        w_resultant = math.sqrt(unit_wt**2 + w_wind**2)
        
        # Calculate working tension per conductor from span and sag or override
        if mode == "direct":
            single_tension = float(c.get("tension_kg", 800.0))
        elif mode == "ratio":
            ratio = float(c.get("tension_ratio", 0.20))
            single_tension = rts_kg * ratio
        else: # "sag_span" (default): Parabolic sag formula with resultant weight T = (w_r * S^2) / (8 * sag)
            # w_r = resultant unit weight (kg/m), span_m = S, sag_m = D
            single_tension = (w_resultant * (span_m ** 2)) / (8.0 * sag_m)
            
        tension_pct_rts = (single_tension / rts_kg * 100.0) if rts_kg > 0 else 0.0
            
        if not enabled:
            conductor_results.append({
                "level": level_num,
                "enabled": False,
                "height_m": height_m,
                "code": c.get("code", "DISABLED"),
                "name": c.get("name", "Disabled Level"),
                "weight_kg_per_m": round(unit_wt, 4),
                "overall_diameter_mm": round(diam_mm, 2),
                "tension_per_cond_kg": 0.0,
                "horizontal_force_kg": 0.0,
                "vertical_weight_kg": 0.0,
                "moment_kg_m": 0.0,
                "num_conductors": num_cond,
                "wind_pressure_kg_m2": round(wind_p, 1),
                "wind_load_kg_per_m": round(w_wind, 4),
                "resultant_weight_kg_m": round(w_resultant, 4)
            })
            continue

        # Horizontal force calculation
        # If line has turn angle theta:
        # F_turn = 2 * T * sin(theta / 2). If theta == 0 (dead end), F_turn = T.
        if abs(angle_deg) > 1e-4:
            rad = math.radians(abs(angle_deg) / 2.0)
            f_turn = 2.0 * single_tension * math.sin(rad) * num_cond
        else:
            # Dead-end termination
            f_turn = single_tension * num_cond

        # Wind load on conductor (if wind pressure given)
        # Projected area = diameter (m) * half-span (m)
        f_wind = 0.0
        if wind_p > 0:
            area_proj = (diam_mm / 1000.0) * (span_m / 2.0) * num_cond
            f_wind = wind_p * area_proj * math.cos(math.radians(angle_deg / 2.0))

        h_force = f_turn + f_wind
        v_weight = unit_wt * (span_m / 2.0) * num_cond
        level_moment = h_force * height_m

        total_conductor_h_force += h_force
        total_overturning_moment += level_moment
        total_conductor_weight += v_weight

        conductor_results.append({
            "level": level_num,
            "enabled": True,
            "height_m": round(height_m, 2),
            "code": c.get("code", "AAC-400"),
            "name": c.get("name", "AAC 400 sq.mm"),
            "weight_kg_per_m": round(unit_wt, 4),
            "overall_diameter_mm": round(diam_mm, 2),
            "span_m": round(span_m, 2),
            "sag_m": round(sag_m, 3),
            "wind_pressure_kg_m2": round(wind_p, 1),
            "wind_load_kg_per_m": round(w_wind, 4),
            "resultant_weight_kg_m": round(w_resultant, 4),
            "single_tension_kg": round(single_tension, 2),
            "tension_per_cond_kg": round(single_tension, 2),
            "tension_pct_rts": round(tension_pct_rts, 1),
            "horizontal_force_kg": round(h_force, 2),
            "vertical_weight_kg": round(v_weight, 2),
            "moment_kg_m": round(level_moment, 2),
            "num_conductors": num_cond,
            "rts_kg": rts_kg,
            "deviation_angle_deg": angle_deg
        })

    # Process Overhead Ground Wire (OHGW - installed over top conductor)
    raw_ohgw = input_data.get("overhead_ground_wire") or input_data.get("ohgw") or {}
    ohgw_code = raw_ohgw.get("code", "GSW-35")
    spec_ohgw = STANDARD_OHGW_SPECS.get(ohgw_code, STANDARD_OHGW_SPECS.get("GSW-35", {}))
    ohgw_enabled = bool(raw_ohgw.get("enabled", False))
    ohgw_height = float(raw_ohgw.get("height_m", 19.1))
    ohgw_num = max(1, int(raw_ohgw.get("num_conductors", raw_ohgw.get("num_wires", 1))))
    ohgw_name = raw_ohgw.get("name", spec_ohgw.get("name", "35 sq.mm Galvanized Steel Strand"))
    ohgw_unit_wt = float(raw_ohgw.get("weight_kg_per_m", spec_ohgw.get("weight_kg_per_m", 0.272)))
    ohgw_rts = float(raw_ohgw.get("breaking_strength_kg", spec_ohgw.get("breaking_strength_kg", 2330.0)))
    ohgw_diam_mm = float(raw_ohgw.get("overall_diameter_mm", spec_ohgw.get("diameter_mm", 7.5)))
    ohgw_span_m = max(1.0, float(raw_ohgw.get("span_m", 80.0)))
    ohgw_sag_m = max(0.01, float(raw_ohgw.get("sag_m", 0.50)))
    ohgw_wind_p = max(0.0, float(raw_ohgw.get("wind_pressure_kg_m2", 0.0)))
    ohgw_angle_deg = float(raw_ohgw.get("deviation_angle_deg", 0.0))
    ohgw_mode = raw_ohgw.get("tension_mode", "sag_span")

    # Wind load per meter on single OHGW: w_wind = P_wind * (diam_mm / 1000)
    ohgw_w_wind = ohgw_wind_p * (ohgw_diam_mm / 1000.0)
    # Resultant unit weight per meter: w_r = sqrt(w^2 + w_wind^2)
    ohgw_w_resultant = math.sqrt(ohgw_unit_wt**2 + ohgw_w_wind**2)

    if ohgw_mode == "direct":
        ohgw_single_t = float(raw_ohgw.get("tension_kg", 245.0))
    elif ohgw_mode == "ratio":
        ratio = float(raw_ohgw.get("tension_ratio", 0.15))
        ohgw_single_t = ohgw_rts * ratio
    else:
        # sag_span with resultant weight T = (w_r * S^2) / (8 * sag)
        ohgw_single_t = (ohgw_w_resultant * (ohgw_span_m ** 2)) / (8.0 * ohgw_sag_m)

    ohgw_pct_rts = (ohgw_single_t / ohgw_rts * 100.0) if ohgw_rts > 0 else 0.0

    if not ohgw_enabled:
        ohgw_result = {
            "enabled": False,
            "height_m": round(ohgw_height, 2),
            "code": ohgw_code,
            "name": ohgw_name,
            "weight_kg_per_m": round(ohgw_unit_wt, 4),
            "breaking_strength_kg": round(ohgw_rts, 2),
            "overall_diameter_mm": round(ohgw_diam_mm, 2),
            "span_m": round(ohgw_span_m, 2),
            "sag_m": round(ohgw_sag_m, 3),
            "wind_pressure_kg_m2": round(ohgw_wind_p, 1),
            "wind_load_kg_per_m": round(ohgw_w_wind, 4),
            "resultant_weight_kg_m": round(ohgw_w_resultant, 4),
            "single_tension_kg": round(ohgw_single_t, 2),
            "tension_pct_rts": round(ohgw_pct_rts, 1),
            "horizontal_force_kg": 0.0,
            "vertical_weight_kg": 0.0,
            "moment_kg_m": 0.0,
            "num_conductors": ohgw_num,
            "rts_kg": ohgw_rts,
            "deviation_angle_deg": ohgw_angle_deg
        }
    else:
        if abs(ohgw_angle_deg) > 1e-4:
            rad = math.radians(abs(ohgw_angle_deg) / 2.0)
            ohgw_f_turn = 2.0 * ohgw_single_t * math.sin(rad) * ohgw_num
        else:
            ohgw_f_turn = ohgw_single_t * ohgw_num

        ohgw_f_wind = 0.0
        if ohgw_wind_p > 0:
            proj = (ohgw_diam_mm / 1000.0) * (ohgw_span_m / 2.0) * ohgw_num
            ohgw_f_wind = ohgw_wind_p * proj * math.cos(math.radians(ohgw_angle_deg / 2.0))

        ohgw_h_force = ohgw_f_turn + ohgw_f_wind
        ohgw_v_weight = ohgw_unit_wt * (ohgw_span_m / 2.0) * ohgw_num
        ohgw_moment = ohgw_h_force * ohgw_height

        total_conductor_h_force += ohgw_h_force
        total_overturning_moment += ohgw_moment
        total_conductor_weight += ohgw_v_weight

        ohgw_result = {
            "enabled": True,
            "height_m": round(ohgw_height, 2),
            "code": ohgw_code,
            "name": ohgw_name,
            "weight_kg_per_m": round(ohgw_unit_wt, 4),
            "breaking_strength_kg": round(ohgw_rts, 2),
            "overall_diameter_mm": round(ohgw_diam_mm, 2),
            "span_m": round(ohgw_span_m, 2),
            "sag_m": round(ohgw_sag_m, 3),
            "wind_pressure_kg_m2": round(ohgw_wind_p, 1),
            "wind_load_kg_per_m": round(ohgw_w_wind, 4),
            "resultant_weight_kg_m": round(ohgw_w_resultant, 4),
            "single_tension_kg": round(ohgw_single_t, 2),
            "tension_pct_rts": round(ohgw_pct_rts, 1),
            "horizontal_force_kg": round(ohgw_h_force, 2),
            "vertical_weight_kg": round(ohgw_v_weight, 2),
            "moment_kg_m": round(ohgw_moment, 2),
            "num_conductors": ohgw_num,
            "rts_kg": ohgw_rts,
            "deviation_angle_deg": ohgw_angle_deg
        }

    # Process Guy Wire Levels (up to 7)
    raw_guys = input_data.get("guy_wires", [])
    active_guys = []
    parsed_guys = []

    for idx, g in enumerate(raw_guys):
        level_num = g.get("level", idx + 1)
        enabled = bool(g.get("enabled", True))
        height_m = float(g.get("height_m", max(2.0, 14.0 - idx * 1.8)))
        # Anchor distance for this level (or global anchor)
        anchor_d = float(g.get("anchor_distance_m", global_anchor_dist))
        if anchor_d <= 0.0:
            anchor_d = global_anchor_dist

        # Level-specific guy wire size & properties
        level_raw_size = float(g.get("size_sqmm", guy_size))
        level_closest = min(STANDARD_GUY_SPECS.keys(), key=lambda s: abs(s - level_raw_size))
        level_spec = STANDARD_GUY_SPECS.get(level_closest, STANDARD_GUY_SPECS[95])

        level_size = float(g.get("size_sqmm", level_spec["size_sqmm"]))
        level_unit_wt = float(g.get("unit_weight_kg_m", level_spec["unit_weight_kg_m"]))
        default_level_rts = guy_rts if abs(level_size - guy_size) < 1.0 else level_spec["default_rts_kg"]
        level_rts = float(g.get("rts_kg", default_level_rts))
        level_area = level_size  # mm^2 nominal area

        slope_len = math.sqrt(height_m**2 + anchor_d**2)
        angle_rad = math.atan2(height_m, anchor_d)
        angle_deg = math.degrees(angle_rad)
        cos_a = anchor_d / slope_len
        sin_a = height_m / slope_len

        guy_item = {
            "level": level_num,
            "enabled": enabled,
            "height_m": height_m,
            "anchor_distance_m": anchor_d,
            "size_sqmm": level_size,
            "unit_weight_kg_m": level_unit_wt,
            "rts_kg": level_rts,
            "area_sqmm": level_area,
            "slope_length_m": slope_len,
            "angle_deg": angle_deg,
            "angle_rad": angle_rad,
            "cos_a": cos_a,
            "sin_a": sin_a,
            "dead_weight_kg": level_unit_wt * slope_len
        }
        parsed_guys.append(guy_item)
        if enabled:
            active_guys.append(guy_item)

    num_active_guys = len(active_guys)
    guy_results = []
    total_guy_tension = 0.0
    total_guy_h_force = 0.0
    total_guy_v_force = 0.0
    total_resisting_moment = 0.0
    total_guy_wire_weight = 0.0

    if num_active_guys > 0 and total_overturning_moment > 0:
        if calc_method == "equal_moment":
            # Each active guy provides equal fraction of overturning moment
            moment_per_guy = total_overturning_moment / num_active_guys
            for g in active_guys:
                th = moment_per_guy / g["height_m"] if g["height_m"] > 0 else 0.0
                t = th / g["cos_a"] if g["cos_a"] > 0 else 0.0
                g["tension_kg"] = t
                g["h_force_kg"] = th
                g["v_force_kg"] = t * g["sin_a"]
                g["moment_kg_m"] = th * g["height_m"]

        elif calc_method == "equal_shear":
            # Each active guy provides equal horizontal resisting shear
            th_per_guy = total_conductor_h_force / num_active_guys
            for g in active_guys:
                t = th_per_guy / g["cos_a"] if g["cos_a"] > 0 else 0.0
                g["tension_kg"] = t
                g["h_force_kg"] = th_per_guy
                g["v_force_kg"] = t * g["sin_a"]
                g["moment_kg_m"] = th_per_guy * g["height_m"]

        else: # "elastic" (Elastic strain compatibility - recommended standard)
            # Tension T_j = M_total * ( (A_j * H_j * cos(a_j)) / S_j ) / SUM( (A_k * H_k^2 * cos^2(a_k)) / S_k )
            sum_denom = sum((g["area_sqmm"] * g["height_m"]**2 * g["cos_a"]**2) / g["slope_length_m"] for g in active_guys)
            if sum_denom > 1e-6:
                for g in active_guys:
                    numerator = (g["area_sqmm"] * g["height_m"] * g["cos_a"]) / g["slope_length_m"]
                    t = total_overturning_moment * (numerator / sum_denom)
                    th = t * g["cos_a"]
                    tv = t * g["sin_a"]
                    m = th * g["height_m"]
                    g["tension_kg"] = t
                    g["h_force_kg"] = th
                    g["v_force_kg"] = tv
                    g["moment_kg_m"] = m
            else:
                for g in active_guys:
                    g["tension_kg"] = 0.0
                    g["h_force_kg"] = 0.0
                    g["v_force_kg"] = 0.0
                    g["moment_kg_m"] = 0.0

    # Build final guy results list including disabled levels
    for g in parsed_guys:
        if not g.get("enabled", False) or num_active_guys == 0 or total_overturning_moment <= 0:
            guy_results.append({
                "level": g["level"],
                "enabled": g.get("enabled", False),
                "size_sqmm": round(g["size_sqmm"], 1),
                "rts_kg": round(g["rts_kg"], 1),
                "height_m": round(g["height_m"], 2),
                "anchor_distance_m": round(g["anchor_distance_m"], 2),
                "slope_length_m": round(g["slope_length_m"], 2),
                "angle_deg": round(g["angle_deg"], 1),
                "tension_kg": 0.0,
                "horizontal_force_kg": 0.0,
                "vertical_force_kg": 0.0,
                "moment_kg_m": 0.0,
                "safety_factor": 999.0 if not g.get("enabled", False) else 0.0,
                "utilization_pct": 0.0,
                "status": "DISABLED" if not g.get("enabled", False) else "NO_LOAD",
                "dead_weight_kg": round(g["dead_weight_kg"], 2)
            })
        else:
            t = g.get("tension_kg", 0.0)
            th = g.get("h_force_kg", 0.0)
            tv = g.get("v_force_kg", 0.0)
            m = g.get("moment_kg_m", 0.0)
            
            level_rts = g["rts_kg"]
            sf = (level_rts / t) if t > 1e-4 else 999.0
            utilization = (t / level_rts) * 100.0 if level_rts > 0 else 0.0

            if sf >= required_sf:
                status = "SAFE"
            elif sf >= 1.5:
                status = "WARNING"
            else:
                status = "OVERLOADED"

            total_guy_tension += t
            total_guy_h_force += th
            total_guy_v_force += tv
            total_resisting_moment += m
            total_guy_wire_weight += g["dead_weight_kg"]

            guy_results.append({
                "level": g["level"],
                "enabled": True,
                "size_sqmm": round(g["size_sqmm"], 1),
                "rts_kg": round(level_rts, 1),
                "height_m": round(g["height_m"], 2),
                "anchor_distance_m": round(g["anchor_distance_m"], 2),
                "slope_length_m": round(g["slope_length_m"], 2),
                "angle_deg": round(g["angle_deg"], 1),
                "tension_kg": round(t, 2),
                "horizontal_force_kg": round(th, 2),
                "vertical_force_kg": round(tv, 2),
                "moment_kg_m": round(m, 2),
                "safety_factor": round(sf, 2),
                "utilization_pct": round(utilization, 1),
                "status": status,
                "dead_weight_kg": round(g["dead_weight_kg"], 2)
            })

    # Anchor Foundation Forces
    anchor_resultant = math.sqrt(total_guy_h_force**2 + total_guy_v_force**2)
    anchor_angle_deg = math.degrees(math.atan2(total_guy_v_force, total_guy_h_force)) if total_guy_h_force > 1e-4 else 90.0

    # Total downward vertical load on pole base (compressive thrust)
    total_downward_thrust = (
        total_guy_v_force +
        pole_weight +
        total_conductor_weight +
        total_guy_wire_weight
    )

    # Net base reactions & balance check
    net_moment = abs(total_overturning_moment - total_resisting_moment)
    net_h_shear = total_conductor_h_force - total_guy_h_force
    moment_balance_pct = ((total_resisting_moment / total_overturning_moment) * 100.0) if total_overturning_moment > 1e-4 else 100.0

    # System overall status
    any_overloaded = any(g["status"] == "OVERLOADED" for g in guy_results if g["enabled"])
    any_warning = any(g["status"] == "WARNING" for g in guy_results if g["enabled"])
    if any_overloaded or num_active_guys == 0:
        overall_status = "OVERLOADED" if any_overloaded else "UNSUPPORTED"
    elif any_warning:
        overall_status = "WARNING"
    else:
        overall_status = "SAFE"

    return {
        "status": overall_status,
        "calculation_method": calc_method,
        "guy_spec": {
            "type": guy_type,
            "name": guy_type,
            "size_sqmm": guy_size,
            "rts_kg": guy_rts,
            "unit_weight_kg_m": guy_unit_wt,
            "required_sf": required_sf
        },
        "pole": {
            "height_m": pole_height,
            "embedment_m": pole_embedment,
            "above_ground_m": round(pole_above_ground, 2),
            "weight_kg": pole_weight
        },
        "anchor": {
            "global_distance_m": global_anchor_dist,
            "total_horizontal_pull_kg": round(total_guy_h_force, 2),
            "total_vertical_uplift_kg": round(total_guy_v_force, 2),
            "resultant_pull_kg": round(anchor_resultant, 2),
            "resultant_angle_deg": round(anchor_angle_deg, 1)
        },
        "pole_base": {
            "total_downward_thrust_kg": round(total_downward_thrust, 2),
            "net_horizontal_shear_kg": round(net_h_shear, 2),
            "net_unbalance_moment_kg_m": round(net_moment, 2),
            "moment_balance_pct": round(moment_balance_pct, 1)
        },
        "summary": {
            "total_conductor_h_force_kg": round(total_conductor_h_force, 2),
            "total_overturning_moment_kg_m": round(total_overturning_moment, 2),
            "total_guy_h_force_kg": round(total_guy_h_force, 2),
            "total_resisting_moment_kg_m": round(total_resisting_moment, 2),
            "total_conductor_weight_kg": round(total_conductor_weight, 2),
            "total_guy_weight_kg": round(total_guy_wire_weight, 2),
            "ohgw_h_force_kg": round(ohgw_result.get("horizontal_force_kg", 0.0), 2),
            "ohgw_moment_kg_m": round(ohgw_result.get("moment_kg_m", 0.0), 2),
            "active_guy_count": num_active_guys
        },
        "overhead_ground_wire": ohgw_result,
        "conductors": conductor_results,
        "guy_wires": guy_results
    }
