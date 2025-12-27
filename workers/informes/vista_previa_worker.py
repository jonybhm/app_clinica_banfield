# auxiliar/workers/vista_previa_worker.py

from acceso_db.conexion import obtener_conexion
from auxiliar.editor_texto.rtf_preview import rtf_a_html_con_libreoffice

def cargar_vista_previa(codigo):
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute("SELECT CMEM FROM dbo.TEXTOS WHERE CODIGO = ?", (codigo,))
    rtf = cur.fetchone()[0]
    conn.close()

    html = rtf_a_html_con_libreoffice(rtf)
    return rtf, html
