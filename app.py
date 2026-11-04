import os
import json
from flask import Flask, render_template, request, jsonify
from database.db import (
    init_db,
    get_all_conductors,
    get_conductor_by_id,
    get_conductor_by_code,
    create_conductor,
    update_conductor,
    delete_conductor,
    get_db_connection
)
from engine import calculate_pole_guy_system, STANDARD_GUY_SPECS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static"
)

# Ensure database is initialized on startup
with app.app_context():
    init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/conductors", methods=["GET"])
def api_get_conductors():
    search = request.args.get("search", "")
    ctype = request.args.get("type", "")
    conductors = get_all_conductors(search=search, conductor_type=ctype)
    return jsonify({"success": True, "data": conductors, "count": len(conductors)})

@app.route("/api/conductors", methods=["POST"])
def api_create_conductor():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No JSON payload provided"}), 400
    
    required_fields = ["code", "name", "conductor_type", "cross_section_sqmm", 
                       "overall_diameter_mm", "weight_kg_per_m", "breaking_strength_kg"]
    for field in required_fields:
        if field not in data or data[field] is None:
            return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
            
    try:
        new_id = create_conductor(data)
        return jsonify({"success": True, "id": new_id, "message": "Conductor created successfully"}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/conductors/<int:conductor_id>", methods=["GET"])
def api_get_conductor(conductor_id):
    cond = get_conductor_by_id(conductor_id)
    if not cond:
        return jsonify({"success": False, "error": "Conductor not found"}), 404
    return jsonify({"success": True, "data": cond})

@app.route("/api/conductors/<int:conductor_id>", methods=["PUT"])
def api_update_conductor(conductor_id):
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No JSON payload provided"}), 400
    try:
        updated = update_conductor(conductor_id, data)
        if not updated:
            return jsonify({"success": False, "error": "Conductor not found or no changes made"}), 404
        return jsonify({"success": True, "message": "Conductor updated successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/conductors/<int:conductor_id>", methods=["DELETE"])
def api_delete_conductor(conductor_id):
    try:
        deleted = delete_conductor(conductor_id)
        if not deleted:
            return jsonify({"success": False, "error": "Conductor not found"}), 404
        return jsonify({"success": True, "message": "Conductor deleted successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/conductors/reset", methods=["POST"])
def api_reset_conductors():
    try:
        init_db(force_reseed=True)
        return jsonify({"success": True, "message": "Database reset to standard seed conductors"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    payload = request.get_json()
    if not payload:
        return jsonify({"success": False, "error": "Missing calculation payload"}), 400
    try:
        results = calculate_pole_guy_system(payload)
        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/guy-wire-specs", methods=["GET"])
def api_guy_wire_specs():
    """Returns standard guy wire specifications for 95, 50, 35, and 25 sq.mm steel strand."""
    return jsonify({"success": True, "specs": STANDARD_GUY_SPECS})

@app.route("/api/default-scenario", methods=["GET"])
def api_default_scenario():
    """Returns a realistic default 7 guy wire & 3 conductor pole configuration."""
    default_data = {
        "scenario_name": "Standard 22m Pole - 7 Guys vs 3 SAC Conductors",
        "pole": {
            "height_m": 22.0,
            "embedment_m": 2.8,
            "weight_kg": 3500.0
        },
        "anchor": {
            "distance_m": 12.0
        },
        "guy_wire_spec": {
            "name": "95 sq.mm Galvanized Steel Strand",
            "size_sqmm": 95.0,
            "rts_kg": 8528.0,  # High Strength grade (PEA/TIS 404)
            "unit_weight_kg_m": 0.764,
            "required_sf": 2.0
        },
        "calculation_method": "elastic",
        "overhead_ground_wire": {
            "enabled": True,
            "code": "GSW-50",
            "name": "50 sq.mm Galvanized Steel Strand",
            "height_m": 19.1,
            "span_m": 50.0,
            "sag_m": 0.50,
            "weight_kg_per_m": 0.392,
            "breaking_strength_kg": 3355.0,
            "overall_diameter_mm": 9.0,
            "num_conductors": 1,
            "wind_pressure_kg_m2": 40.0,
            "deviation_angle_deg": 0.0
        },
        "conductors": [
            {
                "level": 1,
                "enabled": True,
                "height_m": 18.5,
                "code": "SAC-185",
                "name": "Space Aerial Cable 185 sq.mm",
                "breaking_strength_kg": 3120.0,
                "weight_kg_per_m": 0.71,
                "overall_diameter_mm": 22.0,
                "tension_mode": "sag_span",
                "span_m": 50.0,
                "sag_m": 0.60,
                "num_conductors": 1,
                "wind_pressure_kg_m2": 40.0,
                "deviation_angle_deg": 0.0
            },
            {
                "level": 2,
                "enabled": True,
                "height_m": 16.5,
                "code": "SAC-185",
                "name": "Space Aerial Cable 185 sq.mm",
                "breaking_strength_kg": 3120.0,
                "weight_kg_per_m": 0.71,
                "overall_diameter_mm": 22.0,
                "tension_mode": "sag_span",
                "span_m": 50.0,
                "sag_m": 0.60,
                "num_conductors": 1,
                "wind_pressure_kg_m2": 40.0,
                "deviation_angle_deg": 0.0
            },
            {
                "level": 3,
                "enabled": True,
                "height_m": 14.5,
                "code": "SAC-185",
                "name": "Space Aerial Cable 185 sq.mm",
                "breaking_strength_kg": 3120.0,
                "weight_kg_per_m": 0.71,
                "overall_diameter_mm": 22.0,
                "tension_mode": "sag_span",
                "span_m": 50.0,
                "sag_m": 0.60,
                "num_conductors": 1,
                "wind_pressure_kg_m2": 40.0,
                "deviation_angle_deg": 0.0
            }
        ],
        "guy_wires": [
            {"level": 1, "enabled": True, "height_m": 18.5, "anchor_distance_m": 12.0, "size_sqmm": 50.0},
            {"level": 2, "enabled": True, "height_m": 16.5, "anchor_distance_m": 12.0, "size_sqmm": 95.0},
            {"level": 3, "enabled": True, "height_m": 14.5, "anchor_distance_m": 12.0, "size_sqmm": 95.0},
            {"level": 4, "enabled": True, "height_m": 12.5, "anchor_distance_m": 12.0, "size_sqmm": 95.0},
            {"level": 5, "enabled": True, "height_m": 10.5, "anchor_distance_m": 12.0, "size_sqmm": 95.0},
            {"level": 6, "enabled": True, "height_m": 8.5,  "anchor_distance_m": 12.0, "size_sqmm": 95.0},
            {"level": 7, "enabled": True, "height_m": 6.5,  "anchor_distance_m": 12.0, "size_sqmm": 95.0}
        ]
    }
    return jsonify({"success": True, "data": default_data})

if __name__ == "__main__":
    print("Starting Pole Guy Wire Web App on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
