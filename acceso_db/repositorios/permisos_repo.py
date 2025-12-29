# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 19:26:31 2025

@author: Jonathan
"""

# acceso_db/repositorios/permisos_repo.py
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

def tiene_permiso_editar_informes(codigo_usuario):
    """
    Devuelve True si el usuario tiene permisos de edición
    en los programas 65 o 66 (informes)
    """
    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1
        FROM dbo.ADETER
        WHERE CODIGO = ?
          AND NUMPROG IN (65, 66)
          AND TIPOACC = 2
    """, (codigo_usuario,))

    tiene_permiso = cursor.fetchone() is not None
    conn.close()

    return tiene_permiso
