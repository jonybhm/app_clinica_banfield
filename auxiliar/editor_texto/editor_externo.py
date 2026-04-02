#auxiliar/editor_texto/editor_externo.py
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

    # 📁 crear archivo temporal REAL (no NamedTemporaryFile abierto)
    tmp_dir = tempfile.gettempdir()
    tmp_path = os.path.join(tmp_dir, f"rtf_edit_{int(time.time())}.rtf")

    with open(tmp_path, "w", encoding="latin1") as f:
        f.write(rtf_inicial or "")

    log.info(f"Archivo temporal RTF: {tmp_path}")

    # 🚀 abrir LibreOffice
    subprocess.Popen([
        soffice,
        "--writer",
        "--norestore",
        "--nolockcheck",
        tmp_path
    ])

    # 🧠 esperar a que el archivo sea modificado (bloqueo real)
    last_mtime = os.path.getmtime(tmp_path)

    while True:
        time.sleep(1)

        try:
            new_mtime = os.path.getmtime(tmp_path)
            if new_mtime != last_mtime:
                break
        except FileNotFoundError:
            return None  # LO lo borró o falló

    # ⏳ esperar un toque más por seguridad
    time.sleep(1)

    # 📖 leer resultado
    try:
        with open(tmp_path, "r", encoding="latin1") as f:
            rtf_final = f.read()
    except Exception as e:
        log.error(f"Error leyendo archivo: {e}")
        return None

    # 🧹 borrar archivo
    try:
        os.remove(tmp_path)
    except:
        pass

    if not rtf_final.strip():
        return None

    return rtf_final

