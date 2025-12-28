from pathlib import Path
from typing import Optional
from scanner import scan_directories
from custom_logging import logger

# ---------------------------------
# Configuration
# ---------------------------------

SOURCE_DIR = Path("/Users/shrikantsonone/Desktop/Downloads/PhoneRecord")
TARGET_DIR = Path("/Users/shrikantsonone/Desktop/Downloads/PhoneRecord_processed")

MOVE_FILES = True  # FEATURE FLAG

# ---------------------------------
# Entry Point
# ---------------------------------

if __name__ == "__main__":
    logger.info("Starting phone record ingestion")
    scan_directories(SOURCE_DIR, TARGET_DIR, MOVE_FILES)
    logger.info("Ingestion completed")
