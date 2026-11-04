-- Conductor Table
CREATE TABLE IF NOT EXISTS conductors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    conductor_type TEXT NOT NULL,       -- e.g. 'SAC', 'ACSR', 'AAAC', 'AAC'
    cross_section_sqmm REAL NOT NULL,   -- sq.mm
    overall_diameter_mm REAL NOT NULL,  -- mm
    weight_kg_per_m REAL NOT NULL,      -- kg/m
    breaking_strength_kg REAL NOT NULL, -- RTS/UTS in kg
    standard TEXT DEFAULT 'PEA/TIS',    -- e.g. 'PEA', 'TIS', 'ASTM', 'IEC'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Calculation Presets / Saved Scenarios
CREATE TABLE IF NOT EXISTS calculation_scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_name TEXT NOT NULL,
    pole_height_m REAL NOT NULL DEFAULT 22.0,
    pole_embedment_m REAL NOT NULL DEFAULT 2.8,
    pole_weight_kg REAL NOT NULL DEFAULT 3500.0,
    anchor_distance_m REAL NOT NULL DEFAULT 12.0,
    guy_rts_kg REAL NOT NULL DEFAULT 8528.0,
    calculation_method TEXT NOT NULL DEFAULT 'elastic',
    config_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on code and type for fast lookup
CREATE INDEX IF NOT EXISTS idx_conductors_code ON conductors(code);
CREATE INDEX IF NOT EXISTS idx_conductors_type ON conductors(conductor_type);
