import logging
import os
import sys
from datetime import datetime
from pathlib import Path

def get_log_dir():
    # Carpeta segura por usuario
    base = Path(os.getenv("LOCALAPPDATA", Path.home()))
    log_dir = base / "ClinicaBanfield" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir

LOG_DIR = get_log_dir()

LOG_FILE = LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    encoding="utf-8"
)

def log_exception(exc_type, exc_value, exc_tb):
    logging.critical(
        "Excepción no capturada",
        exc_info=(exc_type, exc_value, exc_tb)
    )

sys.excepthook = log_exception
