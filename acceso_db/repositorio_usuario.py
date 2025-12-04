# -*- coding: utf-8 -*-
"""
Created on Wed May 21 19:25:11 2025

@author: Jonathan
"""

#acceso_db/repositorio_usuario.py
from acceso_db.conexion import obtener_conexion
from acceso_db.config import MODO_CONEXION
from acceso_db.conexion import obtener_conexion

def login_usuario(usuario, clave):
    conn = obtener_conexion()
    cursor = conn.cursor()

    if MODO_CONEXION == "access":
        query = """
            SELECT u.CODIGO, u.APELLIDO, u.NIVEL, u.ACTIVO, m.CODMED
            FROM dbo_AUSUARIOS u
            LEFT JOIN dbo_AMEDEJEC m ON u.CODIGO = m.USUHC
            WHERE u.APELLIDO = ? AND u.CONTRA = ? AND u.ACTIVO = 1
        """
    else:  # SQL Server
        query = """
            SELECT u.CODIGO, u.APELLIDO, u.NIVEL, u.ACTIVO, m.CODMED
            FROM dbo.AUSUARIOS u
            LEFT JOIN dbo.AMEDEJEC m ON u.CODIGO = m.USUHC
            WHERE u.APELLIDO = ? AND u.CONTRA = ? AND u.ACTIVO = 1
        """

    cursor.execute(query, (usuario, clave))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        return {
            "CODIGO": resultado.CODIGO,
            "APELLIDO": resultado.APELLIDO.strip(),
            "NIVEL": resultado.NIVEL,
            "CODMED": resultado.CODMED  # ID del profesional
        }
    else:
        return None
    
def obtener_lista_usuarios():
    conn = obtener_conexion()
    cursor = conn.cursor()

    if MODO_CONEXION == "access":
        query = """
            SELECT DISTINCT APELLIDO 
            FROM dbo_AUSUARIOS
            WHERE APELLIDO IS NOT NULL AND ACTIVO = 1
            ORDER BY APELLIDO
        """
    else:
        query = """
            SELECT DISTINCT APELLIDO
            FROM dbo.AUSUARIOS
            WHERE APELLIDO IS NOT NULL AND ACTIVO = 1
            ORDER BY APELLIDO
        """
    cursor.execute(query)
    resultados = [row[0].strip() for row in cursor.fetchall()]
    conn.close()
    return resultados



def obtener_usuarios_con_codigo():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT CODIGO, APELLIDO
        FROM dbo.AUSUARIOS
        WHERE ACTIVO = 1
    """)
    rows = cursor.fetchall()
    conn.close()
    return [(row.CODIGO, row.APELLIDO) for row in rows]
