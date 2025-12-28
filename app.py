import logging
import re
import shutil
import sqlite3
from pathlib import Path
from typing import Optional

from pymediainfo import MediaInfo

# ---------------------------------
# Configuration
# ---------------------------------

SOURCE_DIR = Path("/path/to/source")
TARGET_DIR = Path("/path/to/archive")
DB_PATH = Path("phone_records.db")

MOVE_FILES = True  # FEATURE FLAG

AAC_REGEX = re.compile(
    r"(?P<contact>.*)-"
    r"(?P<year>\d{4})"
    r"(?P<month>\d{2})"
    r"(?P<day>\d{2})"
    r"(?P<hour>\d{2})"
    r"(?P<minute>\d{2})"
    r"(?P<seconds>\d{2})\.aac$",
    re.IGNORECASE,
)

LOG_FILE = "phone_record_ingest.log"

# ---------------------------------
# Logging
# ---------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ],
)

logger = logging.getLogger(__name__)

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


# ---------------------------------
# Metadata Extraction
# ---------------------------------

def extract_aac_metadata(file_path: Path) -> dict:
    media_info = MediaInfo.parse(file_path)

    audio_track = next(
        (t for t in media_info.tracks if t.track_type == "Audio"),
        None,
    )

    if not audio_track:
        raise ValueError("No audio track found")

    return {
        "duration_seconds": (
            audio_track.duration / 1000 if audio_track.duration else None
        ),
        "bitrate": audio_track.bit_rate,
        "sample_rate": audio_track.sampling_rate,
        "channels": audio_track.channel_s,
        "file_size_bytes": file_path.stat().st_size,
    }


# ---------------------------------
# Core Processing
# ---------------------------------

def process_file(file_path: Path, conn: sqlite3.Connection) -> None:
    match = AAC_REGEX.match(file_path.name)

    if not match:
        logger.warning("Filename regex failed: %s", file_path.name)
        return

    data = match.groupdict()

    try:
        audio_meta = extract_aac_metadata(file_path)
    except Exception as exc:
        logger.error("Metadata extraction failed for %s: %s", file_path.name, exc)
        return

    record = {
        "filename": file_path.name,
        "contact": data["contact"],
        "year": int(data["year"]),
        "month": int(data["month"]),
        "day": int(data["day"]),
        "hour": int(data["hour"]),
        "minute": int(data["minute"]),
        "second": int(data["seconds"]),
        **audio_meta,
    }

    conn.execute(
        """
        INSERT INTO phone_records (
            filename, contact,
            year, month, day,
            hour, minute, second,
            duration_seconds, bitrate,
            sample_rate, channels,
            file_size_bytes
        )
        VALUES (
            :filename, :contact,
            :year, :month, :day,
            :hour, :minute, :second,
            :duration_seconds, :bitrate,
            :sample_rate, :channels,
            :file_size_bytes
        )
        """,
        record,
    )
    conn.commit()

    logger.info("Inserted DB record for %s", file_path.name)

    if MOVE_FILES:
        dest_dir = TARGET_DIR / data["year"] / data["month"]
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest_path = dest_dir / file_path.name
        shutil.move(str(file_path), str(dest_path))

        logger.info("Moved file to %s", dest_path)


def scan_directories() -> None:
    conn = init_db(DB_PATH)

    for path in SOURCE_DIR.rglob("*.aac"):
        if path.is_file():
            process_file(path, conn)

    conn.close()


# ---------------------------------
# Entry Point
# ---------------------------------

if __name__ == "__main__":
    logger.info("Starting phone record ingestion")
    scan_directories()
    logger.info("Ingestion completed")
