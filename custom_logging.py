import logging

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

