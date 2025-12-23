import subprocess
import tempfile
import os
import time
import logging

LIBREOFFICE_PATHS = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
]

log = logging.getLogger(__name__)


def buscar_libreoffice():
    for path in LIBREOFFICE_PATHS:
        if os.path.exists(path):
            return path
    return None


def editar_rtf_con_libreoffice(rtf_inicial: str) -> str | None:
    soffice = buscar_libreoffice()
    if not soffice:
        raise FileNotFoundError("LibreOffice no encontrado")

    # ---- archivo temporal ----
    tmp = tempfile.NamedTemporaryFile(
        suffix=".rtf", delete=False, mode="w", encoding="latin1"
    )
    tmp.write(rtf_inicial or "")
    tmp.close()

    log.info(f"Archivo temporal RTF: {tmp.name}")

    # ---- abrir LibreOffice ----
    proc = subprocess.Popen(
        [soffice, "--writer", tmp.name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # ---- esperar a que cierre ----
    proc.wait()

    # ---- leer resultado ----
    try:
        with open(tmp.name, "r", encoding="latin1") as f:
            rtf_final = f.read()
    finally:
        os.remove(tmp.name)

    if not rtf_final.strip():
        log.info("Edición cancelada o archivo vacío")
        return None

    return rtf_final

