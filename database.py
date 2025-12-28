import sqlite3
from pathlib import Path

# ---------------------------------
# Database
# ---------------------------------

def init_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS phone_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            contact TEXT NOT NULL,
            year INTEGER,
            month INTEGER,
            day INTEGER,
            hour INTEGER,
            minute INTEGER,
            second INTEGER,
            duration_seconds REAL,
            bitrate INTEGER,
            sample_rate INTEGER,
            channels INTEGER,
            file_size_bytes INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    return conn
