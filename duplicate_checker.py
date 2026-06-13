import hashlib
import json
from database import get_connection

def generate_hash(record: dict) -> str:
    """
    Generate a SHA-256 hash from normalized record content.
    Ignores key order and extra whitespace.
    """
    normalized = {
        "name":     record.get("name", "").strip().lower(),
        "email":    record.get("email", "").strip().lower(),
        "category": record.get("category", "").strip().lower(),
        "value":    str(record.get("value", "")).strip()
    }
    record_str = json.dumps(normalized, sort_keys=True)
    return hashlib.sha256(record_str.encode()).hexdigest()

def is_duplicate(data_hash: str) -> bool:
    """Check if this hash already exists in cloud_records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM cloud_records WHERE data_hash = ?", (data_hash,)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None

def log_rejection(raw_data: str, reason: str):
    """Log rejected records to the rejected_records table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO rejected_records (raw_data, reason) VALUES (?, ?)",
        (str(raw_data), reason)
    )
    conn.commit()
    conn.close()

def log_audit(action: str, record_hash: str, message: str):
    """Append to audit log."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO audit_log (action, record_hash, message) VALUES (?, ?, ?)",
        (action, record_hash, message)
    )
    conn.commit()
    conn.close()