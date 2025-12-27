from acceso_db.conexion import obtener_conexion

def cargar_modelos():
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute("SELECT CODIGO, DESCRIPCION FROM dbo.TEXTOS ORDER BY DESCRIPCION")
    data = cur.fetchall()
    conn.close()
    return data