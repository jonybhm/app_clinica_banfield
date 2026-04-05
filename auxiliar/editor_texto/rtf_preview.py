#auxiliar/editor_texto/rtf_preview.py
import subprocess
import tempfile
import os
import shutil

from auxiliar.editor_texto.editor_externo import buscar_libreoffice

LIBREOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"

def rtf_a_html_con_libreoffice(rtf_texto: str) -> str | None:
    with tempfile.TemporaryDirectory() as tmp:
        rtf_path = os.path.join(tmp, "doc.rtf")
        html_path = os.path.join(tmp, "doc.html")

        # Guardar RTF
        with open(rtf_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(rtf_texto)

        # Convertir
        subprocess.run(
            [
                LIBREOFFICE_PATH,
                "--headless",
                "--convert-to", "html",
                "--outdir", tmp,
                rtf_path
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

        if not os.path.exists(html_path):
            return None

        with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()

        return html
    
def html_a_rtf_con_libreoffice(html: str) -> str:
    import tempfile
    import subprocess
    import os
    import time

    soffice = buscar_libreoffice()
    if not soffice:
        raise Exception("LibreOffice no encontrado")

    with tempfile.TemporaryDirectory() as tmp_dir:
        html_path = os.path.join(tmp_dir, "doc.html")
        odt_path = os.path.join(tmp_dir, "doc.odt")
        rtf_path = os.path.join(tmp_dir, "doc.rtf")

        # 1️⃣ Guardar HTML
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)

        # 2️⃣ HTML → ODT (SIEMPRE funciona)
        subprocess.run([
            soffice,
            "--headless",
            "--convert-to", "odt",
            "--outdir", tmp_dir,
            html_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # esperar ODT
        for _ in range(10):
            if os.path.exists(odt_path):
                break
            time.sleep(0.5)

        if not os.path.exists(odt_path):
            raise Exception("LibreOffice no generó ODT")

        # 3️⃣ ODT → RTF
        subprocess.run([
            soffice,
            "--headless",
            "--convert-to", "rtf",
            "--outdir", tmp_dir,
            odt_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # esperar RTF
        for _ in range(10):
            if os.path.exists(rtf_path):
                break
            time.sleep(0.5)

        if not os.path.exists(rtf_path):
            raise Exception("LibreOffice no generó RTF desde ODT")

        # 4️⃣ Leer resultado
        with open(rtf_path, "r", encoding="latin1", errors="ignore") as f:
            return f.read()