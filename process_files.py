import re
import shutil
from pathlib import Path
import sqlite3

from custom_logging import logger
from metadata import extract_aac_metadata
from config import MONTH_NAMES

# ---------------------------------
# Core Processing
# ---------------------------------
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

def get_month_dir(month: str) -> str:
    return f"{month} {MONTH_NAMES[month]}"

def process_file(file_path: Path, conn: sqlite3.Connection, TARGET_DIR, MOVE_FILES) -> None:
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
        month_dir = get_month_dir(data["month"])

        dest_dir = (
            TARGET_DIR
            / data["year"]
            / month_dir
        )

        dest_dir.mkdir(parents=True, exist_ok=True)

        dest_path = dest_dir / file_path.name
        shutil.copy(str(file_path), str(dest_path))

        logger.info("Moved file to %s", dest_path)


