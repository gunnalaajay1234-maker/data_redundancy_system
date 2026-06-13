import sqlite3
import os

DB_PATH = "cloud_storage.db"

def init_db():
    """Initialize the cloud database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Main cloud records table (unique data only)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cloud_records (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            email       TEXT NOT NULL,
            data_hash   TEXT NOT NULL UNIQUE,   -- SHA256 hash for dedup
            category    TEXT,
            value       REAL,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_verified INTEGER DEFAULT 1
        )
    """)

    # Rejected records log (duplicates + invalid)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rejected_records (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_data    TEXT,
            reason      TEXT,
            rejected_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Audit log for every incoming entry
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            action      TEXT,
            record_hash TEXT,
            message     TEXT,
            timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully.")

def get_connection():
    return sqlite3.connect(DB_PATH)