from pathlib import Path
from database import init_db
from process_files import process_file

DB_PATH = Path("phone_records.db")

def scan_directories(SOURCE_DIR, TARGET_DIR, MOVE_FILES) -> None:
    conn = init_db(DB_PATH)

    for path in SOURCE_DIR.rglob("*.aac"):
        if path.is_file():
            process_file(path, conn, TARGET_DIR, MOVE_FILES)

    conn.close()
