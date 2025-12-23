import logging
import os
import sys
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(
    LOG_DIR,
    f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    encoding="utf-8"
)

def log_exception(exc_type, exc_value, exc_tb):
    logging.critical(
        "Excepción no capturada",
        exc_info=(exc_type, exc_value, exc_tb)
    )

# Hook global
sys.excepthook = log_exception