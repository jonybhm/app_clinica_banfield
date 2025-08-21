# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 19:26:31 2025

@author: Jonathan
"""


from acceso_db.conexion import obtener_conexion

def tiene_permiso_admin(codigo_usuario):
    """
    Devuelve True si el usuario tiene acceso TOTAL al programa 16 (MANT. USUARIOS DEL SIST.)
    """
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TIPOACC 
        FROM dbo.ADETER
        WHERE CODIGO = ? AND NUMPROG = 16
    """, (codigo_usuario,))
    row = cursor.fetchone()
    conn.close()
    return row and row[0] == 2
