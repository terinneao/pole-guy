import os
import sqlite3
from typing import List, Dict, Any, Optional
from database.seed_data import DEFAULT_CONDUCTORS

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "conductors.db")
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")

def get_db_connection() -> sqlite3.Connection:
    """Create a database connection with dict-like row access and 30s timeout."""
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(force_reseed: bool = False):
    """Initialize database tables and seed with standard conductors if empty."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Read and execute schema
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        cursor.executescript(schema_sql)

        # Check if conductors table is empty
        cursor.execute("SELECT COUNT(*) FROM conductors")
        count = cursor.fetchone()[0]

        if force_reseed:
            cursor.execute("DELETE FROM conductors")
        
        insert_sql = """
            INSERT OR IGNORE INTO conductors 
            (code, name, conductor_type, cross_section_sqmm, overall_diameter_mm, 
             weight_kg_per_m, breaking_strength_kg, standard, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        for c in DEFAULT_CONDUCTORS:
            cursor.execute(insert_sql, (
                c["code"],
                c["name"],
                c["conductor_type"],
                c["cross_section_sqmm"],
                c["overall_diameter_mm"],
                c["weight_kg_per_m"],
                c["breaking_strength_kg"],
                c.get("standard", "PEA/TIS"),
                c.get("notes", "")
            ))
        conn.commit()
    finally:
        conn.close()

def get_all_conductors(search: Optional[str] = None, conductor_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve conductors with optional search and type filtering."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        query = "SELECT * FROM conductors WHERE 1=1"
        params = []

        if conductor_type and conductor_type.strip() and conductor_type.lower() != 'all':
            query += " AND conductor_type = ?"
            params.append(conductor_type.strip())

        if search and search.strip():
            query += " AND (code LIKE ? OR name LIKE ? OR standard LIKE ?)"
            s = f"%{search.strip()}%"
            params.extend([s, s, s])

        query += " ORDER BY conductor_type, cross_section_sqmm ASC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def get_conductor_by_id(conductor_id: int) -> Optional[Dict[str, Any]]:
    """Get single conductor by ID."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conductors WHERE id = ?", (conductor_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_conductor_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Get single conductor by Code."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conductors WHERE code = ?", (code,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def create_conductor(data: Dict[str, Any]) -> int:
    """Insert a new conductor."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        insert_sql = """
            INSERT INTO conductors 
            (code, name, conductor_type, cross_section_sqmm, overall_diameter_mm, 
             weight_kg_per_m, breaking_strength_kg, standard, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(insert_sql, (
            str(data["code"]).strip(),
            str(data["name"]).strip(),
            str(data["conductor_type"]).strip().upper(),
            float(data["cross_section_sqmm"]),
            float(data["overall_diameter_mm"]),
            float(data["weight_kg_per_m"]),
            float(data["breaking_strength_kg"]),
            str(data.get("standard", "Custom")).strip(),
            str(data.get("notes", "")).strip()
        ))
        new_id = cursor.lastrowid
        conn.commit()
        return new_id
    finally:
        conn.close()

def update_conductor(conductor_id: int, data: Dict[str, Any]) -> bool:
    """Update an existing conductor."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        update_sql = """
            UPDATE conductors 
            SET code = ?, name = ?, conductor_type = ?, cross_section_sqmm = ?, 
                overall_diameter_mm = ?, weight_kg_per_m = ?, breaking_strength_kg = ?, 
                standard = ?, notes = ?
            WHERE id = ?
        """
        cursor.execute(update_sql, (
            str(data["code"]).strip(),
            str(data["name"]).strip(),
            str(data["conductor_type"]).strip().upper(),
            float(data["cross_section_sqmm"]),
            float(data["overall_diameter_mm"]),
            float(data["weight_kg_per_m"]),
            float(data["breaking_strength_kg"]),
            str(data.get("standard", "Custom")).strip(),
            str(data.get("notes", "")).strip(),
            conductor_id
        ))
        rows_affected = cursor.rowcount
        conn.commit()
        return rows_affected > 0
    finally:
        conn.close()

def delete_conductor(conductor_id: int) -> bool:
    """Delete a conductor by ID."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM conductors WHERE id = ?", (conductor_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        return rows_affected > 0
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}. Total conductors: {len(get_all_conductors())}")
