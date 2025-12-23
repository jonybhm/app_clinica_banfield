import subprocess
import tempfile
import os
import shutil

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
