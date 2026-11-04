"""
Seed data for conductors database.
Standard conductors commonly used in distribution and transmission lines (PEA, MEA, IEC, ASTM).
Units: kg, meter, mm, sq.mm.
"""

DEFAULT_CONDUCTORS = [
    # SAC (Space Aerial Cable - 22/33 kV XLPE Insulated Aluminum)
    {
        "code": "SAC-50",
        "name": "Space Aerial Cable 50 sq.mm",
        "conductor_type": "SAC",
        "cross_section_sqmm": 50.0,
        "overall_diameter_mm": 14.5,
        "weight_kg_per_m": 0.240,
        "breaking_strength_kg": 860.0,
        "standard": "PEA/TIS",
        "notes": "22/33 kV partially insulated overhead conductor"
    },
    {
        "code": "SAC-95",
        "name": "Space Aerial Cable 95 sq.mm",
        "conductor_type": "SAC",
        "cross_section_sqmm": 95.0,
        "overall_diameter_mm": 17.5,
        "weight_kg_per_m": 0.390,
        "breaking_strength_kg": 1630.0,
        "standard": "PEA/TIS",
        "notes": "22/33 kV partially insulated overhead conductor"
    },
    {
        "code": "SAC-185",
        "name": "Space Aerial Cable 185 sq.mm",
        "conductor_type": "SAC",
        "cross_section_sqmm": 185.0,
        "overall_diameter_mm": 22.0,
        "weight_kg_per_m": 0.710,
        "breaking_strength_kg": 3120.0,
        "standard": "PEA/TIS",
        "notes": "22/33 kV main feeder distribution line"
    },
    {
        "code": "SAC-240",
        "name": "Space Aerial Cable 240 sq.mm",
        "conductor_type": "SAC",
        "cross_section_sqmm": 240.0,
        "overall_diameter_mm": 25.0,
        "weight_kg_per_m": 0.900,
        "breaking_strength_kg": 4050.0,
        "standard": "PEA/TIS",
        "notes": "22/33 kV heavy feeder line"
    },
    {
        "code": "SAC-400",
        "name": "Space Aerial Cable 400 sq.mm",
        "conductor_type": "SAC",
        "cross_section_sqmm": 400.0,
        "overall_diameter_mm": 30.5,
        "weight_kg_per_m": 1.460,
        "breaking_strength_kg": 6750.0,
        "standard": "PEA/TIS",
        "notes": "22/33 kV extra heavy feeder"
    },

    # ACSR (Aluminum Conductor Steel Reinforced)
    {
        "code": "ACSR-25",
        "name": "ACSR 25 sq.mm (6/1)",
        "conductor_type": "ACSR",
        "cross_section_sqmm": 24.3,
        "overall_diameter_mm": 6.42,
        "weight_kg_per_m": 0.085,
        "breaking_strength_kg": 715.0,
        "standard": "TIS/IEC",
        "notes": "Light distribution / rural line"
    },
    {
        "code": "ACSR-35",
        "name": "ACSR 35 sq.mm (6/1)",
        "conductor_type": "ACSR",
        "cross_section_sqmm": 34.3,
        "overall_diameter_mm": 7.56,
        "weight_kg_per_m": 0.120,
        "breaking_strength_kg": 1000.0,
        "standard": "TIS/IEC",
        "notes": "Distribution branch line"
    },
    {
        "code": "ACSR-50",
        "name": "ACSR 50 sq.mm (6/1)",
        "conductor_type": "ACSR",
        "cross_section_sqmm": 48.3,
        "overall_diameter_mm": 9.00,
        "weight_kg_per_m": 0.169,
        "breaking_strength_kg": 1390.0,
        "standard": "TIS/IEC",
        "notes": "Medium distribution line"
    },
    {
        "code": "ACSR-70",
        "name": "ACSR 70 sq.mm (6/1)",
        "conductor_type": "ACSR",
        "cross_section_sqmm": 68.3,
        "overall_diameter_mm": 10.70,
        "weight_kg_per_m": 0.239,
        "breaking_strength_kg": 1930.0,
        "standard": "TIS/IEC",
        "notes": "Distribution feeder"
    },
    {
        "code": "ACSR-95",
        "name": "ACSR 95 sq.mm (6/1)",
        "conductor_type": "ACSR",
        "cross_section_sqmm": 93.3,
        "overall_diameter_mm": 12.50,
        "weight_kg_per_m": 0.326,
        "breaking_strength_kg": 2630.0,
        "standard": "TIS/IEC",
        "notes": "Standard primary distribution"
    },
    {
        "code": "ACSR-120",
        "name": "ACSR 120 sq.mm (26/7)",
        "conductor_type": "ACSR",
        "cross_section_sqmm": 119.5,
        "overall_diameter_mm": 14.80,
        "weight_kg_per_m": 0.448,
        "breaking_strength_kg": 3690.0,
        "standard": "TIS/IEC",
        "notes": "Substation exit / feeder"
    },
    {
        "code": "ACSR-185",
        "name": "ACSR 185 sq.mm (26/7)",
        "conductor_type": "ACSR",
        "cross_section_sqmm": 186.2,
        "overall_diameter_mm": 18.50,
        "weight_kg_per_m": 0.702,
        "breaking_strength_kg": 5740.0,
        "standard": "TIS/IEC",
        "notes": "Heavy feeder / sub-transmission"
    },
    {
        "code": "ACSR-240",
        "name": "ACSR 240 sq.mm (26/7)",
        "conductor_type": "ACSR",
        "cross_section_sqmm": 241.6,
        "overall_diameter_mm": 21.00,
        "weight_kg_per_m": 0.908,
        "breaking_strength_kg": 7450.0,
        "standard": "TIS/IEC",
        "notes": "69/115 kV transmission line"
    },
    {
        "code": "ACSR-300",
        "name": "ACSR 300 sq.mm (26/7)",
        "conductor_type": "ACSR",
        "cross_section_sqmm": 299.4,
        "overall_diameter_mm": 23.50,
        "weight_kg_per_m": 1.130,
        "breaking_strength_kg": 9230.0,
        "standard": "TIS/IEC",
        "notes": "115 kV transmission line"
    },
    {
        "code": "ACSR-400",
        "name": "ACSR 400 sq.mm (54/7)",
        "conductor_type": "ACSR",
        "cross_section_sqmm": 399.7,
        "overall_diameter_mm": 26.80,
        "weight_kg_per_m": 1.345,
        "breaking_strength_kg": 10700.0,
        "standard": "TIS/IEC",
        "notes": "115/230 kV transmission line"
    },
    {
        "code": "ACSR-477-HAWK",
        "name": "ACSR 477 MCM Hawk (26/7)",
        "conductor_type": "ACSR",
        "cross_section_sqmm": 241.7,
        "overall_diameter_mm": 21.79,
        "weight_kg_per_m": 0.977,
        "breaking_strength_kg": 8850.0,
        "standard": "ASTM B232",
        "notes": "North American standard code 'Hawk'"
    },
    {
        "code": "ACSR-795-DRAKE",
        "name": "ACSR 795 MCM Drake (26/7)",
        "conductor_type": "ACSR",
        "cross_section_sqmm": 402.8,
        "overall_diameter_mm": 28.14,
        "weight_kg_per_m": 1.628,
        "breaking_strength_kg": 14300.0,
        "standard": "ASTM B232",
        "notes": "High capacity transmission code 'Drake'"
    },
    {
        "code": "ACSR-1272-PHEASANT",
        "name": "ACSR 1272 MCM Pheasant (54/19)",
        "conductor_type": "ACSR",
        "cross_section_sqmm": 644.5,
        "overall_diameter_mm": 35.10,
        "weight_kg_per_m": 2.457,
        "breaking_strength_kg": 19700.0,
        "standard": "ASTM B232",
        "notes": "Extra-high capacity transmission code 'Pheasant'"
    },

    # AAAC (All Aluminum Alloy Conductor)
    {
        "code": "AAAC-50",
        "name": "AAAC 50 sq.mm",
        "conductor_type": "AAAC",
        "cross_section_sqmm": 49.5,
        "overall_diameter_mm": 9.00,
        "weight_kg_per_m": 0.136,
        "breaking_strength_kg": 1460.0,
        "standard": "TIS/IEC",
        "notes": "Corrosion resistant coastal distribution"
    },
    {
        "code": "AAAC-95",
        "name": "AAAC 95 sq.mm",
        "conductor_type": "AAAC",
        "cross_section_sqmm": 93.3,
        "overall_diameter_mm": 12.40,
        "weight_kg_per_m": 0.256,
        "breaking_strength_kg": 2750.0,
        "standard": "TIS/IEC",
        "notes": "Coastal & industrial primary distribution"
    },
    {
        "code": "AAAC-185",
        "name": "AAAC 185 sq.mm",
        "conductor_type": "AAAC",
        "cross_section_sqmm": 181.6,
        "overall_diameter_mm": 17.50,
        "weight_kg_per_m": 0.500,
        "breaking_strength_kg": 5350.0,
        "standard": "TIS/IEC",
        "notes": "High strength alloy feeder"
    },
    {
        "code": "AAAC-240",
        "name": "AAAC 240 sq.mm",
        "conductor_type": "AAAC",
        "cross_section_sqmm": 242.5,
        "overall_diameter_mm": 20.20,
        "weight_kg_per_m": 0.667,
        "breaking_strength_kg": 7150.0,
        "standard": "TIS/IEC",
        "notes": "Transmission alloy conductor"
    },

    # AAC (All Aluminum Conductor)
    {
        "code": "AAC-95",
        "name": "AAC 95 sq.mm",
        "conductor_type": "AAC",
        "cross_section_sqmm": 93.3,
        "overall_diameter_mm": 12.40,
        "weight_kg_per_m": 0.254,
        "breaking_strength_kg": 1580.0,
        "standard": "TIS/IEC",
        "notes": "Short span distribution"
    },
    {
        "code": "AAC-185",
        "name": "AAC 185 sq.mm",
        "conductor_type": "AAC",
        "cross_section_sqmm": 181.6,
        "overall_diameter_mm": 17.50,
        "weight_kg_per_m": 0.495,
        "breaking_strength_kg": 3080.0,
        "standard": "TIS/IEC",
        "notes": "Medium span distribution"
    },
    {
        "code": "AAC-240",
        "name": "AAC 240 sq.mm",
        "conductor_type": "AAC",
        "cross_section_sqmm": 242.5,
        "overall_diameter_mm": 20.20,
        "weight_kg_per_m": 0.660,
        "breaking_strength_kg": 4110.0,
        "standard": "TIS/IEC",
        "notes": "Substation bus / jumper conductor"
    },
    {
        "code": "AAC-400",
        "name": "AAC 400 sq.mm",
        "conductor_type": "AAC",
        "cross_section_sqmm": 400.0,
        "overall_diameter_mm": 26.00,
        "weight_kg_per_m": 1.100,
        "breaking_strength_kg": 6680.0,
        "standard": "TIS/IEC",
        "notes": "Substation bus / heavy distribution feeder"
    }
]
