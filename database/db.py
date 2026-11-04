import os
import sqlite3
import shutil
import tempfile
from typing import List, Dict, Any, Optional
from database.seed_data import DEFAULT_CONDUCTORS

DB_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")
SOURCE_DB_PATH = os.path.join(DB_DIR, "conductors.db")
DB_PATH = SOURCE_DB_PATH  # Maintained for backwards compatibility

def is_running_on_vercel() -> bool:
    """Check if the environment is Vercel, AWS Lambda, or a read-only filesystem."""
    if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return True
    try:
        test_file = os.path.join(DB_DIR, ".write_test")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        return False
    except (OSError, IOError, PermissionError):
        return True

def get_db_path() -> str:
    """
    Returns the appropriate path for the SQLite database.
    On Vercel / serverless / read-only environments, uses tempfile.gettempdir()/conductors.db.
    Copies existing DB if available or initializes fresh from schema/seed.
    """
    if is_running_on_vercel():
        tmp_db = os.path.join(tempfile.gettempdir(), "conductors.db")
        if not os.path.exists(tmp_db):
            if os.path.exists(SOURCE_DB_PATH):
                try:
                    shutil.copyfile(SOURCE_DB_PATH, tmp_db)
                except Exception:
                    pass
        return tmp_db
    return SOURCE_DB_PATH

def get_db_connection() -> sqlite3.Connection:
    """Create a database connection with dict-like row access."""
    db_path = get_db_path()
    # Ensure database file exists if in /tmp
    if is_running_on_vercel() and not os.path.exists(db_path):
        init_db()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(force_reseed: bool = False):
    """Initialize database tables and seed with standard conductors if empty."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
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
        count = 0

    if count == 0:
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

    conn.close()

def get_all_conductors(search: Optional[str] = None, conductor_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve conductors with optional search and type filtering."""
    conn = get_db_connection()
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
    result = [dict(row) for row in rows]
    conn.close()
    return result

def get_conductor_by_id(conductor_id: int) -> Optional[Dict[str, Any]]:
    """Get single conductor by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conductors WHERE id = ?", (conductor_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_conductor_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Get single conductor by Code."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conductors WHERE code = ?", (code,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_conductor(data: Dict[str, Any]) -> int:
    """Insert a new conductor."""
    conn = get_db_connection()
    cursor = conn.cursor()
    insert_sql = """
        INSERT INTO conductors 
        (code, name, conductor_type, cross_section_sqmm, overall_diameter_mm, 
         weight_kg_per_m, breaking_strength_kg, standard, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(insert_sql, (
        data["code"].strip(),
        data["name"].strip(),
        data["conductor_type"].strip().upper(),
        float(data["cross_section_sqmm"]),
        float(data["overall_diameter_mm"]),
        float(data["weight_kg_per_m"]),
        float(data["breaking_strength_kg"]),
        data.get("standard", "Custom").strip(),
        data.get("notes", "").strip()
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def update_conductor(conductor_id: int, data: Dict[str, Any]) -> bool:
    """Update an existing conductor."""
    conn = get_db_connection()
    cursor = conn.cursor()
    update_sql = """
        UPDATE conductors 
        SET code = ?, name = ?, conductor_type = ?, cross_section_sqmm = ?, 
            overall_diameter_mm = ?, weight_kg_per_m = ?, breaking_strength_kg = ?, 
            standard = ?, notes = ?
        WHERE id = ?
    """
    cursor.execute(update_sql, (
        data["code"].strip(),
        data["name"].strip(),
        data["conductor_type"].strip().upper(),
        float(data["cross_section_sqmm"]),
        float(data["overall_diameter_mm"]),
        float(data["weight_kg_per_m"]),
        float(data["breaking_strength_kg"]),
        data.get("standard", "Custom").strip(),
        data.get("notes", "").strip(),
        conductor_id
    ))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def delete_conductor(conductor_id: int) -> bool:
    """Delete a conductor by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conductors WHERE id = ?", (conductor_id,))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {get_db_path()}. Total conductors: {len(get_all_conductors())}")
