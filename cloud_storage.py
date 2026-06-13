from database import get_connection
from duplicate_checker import generate_hash, is_duplicate, log_rejection, log_audit

def store_record(record: dict) -> dict:
    """
    Store a validated, unique record into cloud_records.
    Returns a result dict with status and message.
    """
    data_hash = generate_hash(record)

    if is_duplicate(data_hash):
        reason = f"Duplicate detected for email '{record.get('email')}'"
        log_rejection(record, reason)
        log_audit("REJECTED_DUPLICATE", data_hash, reason)
        return {"status": "duplicate", "message": reason}

    # Store unique record
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO cloud_records (name, email, data_hash, category, value)
            VALUES (?, ?, ?, ?, ?)
        """, (
            record["name"].strip(),
            record["email"].strip().lower(),
            data_hash,
            record["category"].strip().lower(),
            float(record["value"])
        ))
        conn.commit()
        log_audit("STORED", data_hash, f"New record stored for '{record['email']}'")
        return {"status": "success", "message": f"Record stored successfully (hash: {data_hash[:12]}...)"}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

def fetch_all_records():
    """Return all stored unique cloud records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, email, category, value, created_at FROM cloud_records ORDER BY id"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_rejected():
    """Return all rejected records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, raw_data, reason, rejected_at FROM rejected_records ORDER BY id"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows