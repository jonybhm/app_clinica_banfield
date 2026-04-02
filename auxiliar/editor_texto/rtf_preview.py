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

    tmp_html = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    tmp_rtf = tmp_html.name.replace(".html", ".rtf")

    with open(tmp_html.name, "w", encoding="utf-8") as f:
        f.write(html)

    soffice = buscar_libreoffice()

    subprocess.run([
        soffice,
        "--headless",
        "--convert-to", "rtf",
        tmp_html.name,
        "--outdir", os.path.dirname(tmp_html.name)
    ])

    with open(tmp_rtf, "r", encoding="latin1") as f:
        contenido = f.read()

    os.remove(tmp_html.name)
    os.remove(tmp_rtf)

    return contenido