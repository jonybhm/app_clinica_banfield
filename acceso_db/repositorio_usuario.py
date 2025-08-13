# -*- coding: utf-8 -*-
"""
Created on Wed May 21 19:25:11 2025

@author: Jonathan
"""
from acceso_db.conexion import obtener_conexion
from acceso_db.config import MODO_CONEXION

def login_usuario(usuario, clave):
    conn = obtener_conexion()
    cursor = conn.cursor()

    if MODO_CONEXION == "access":
        query = """
            SELECT u.CODIGO, u.APELLIDO, u.NIVEL, u.ACTIVO, m.CODMED
            FROM dbo_AUSUARIOS u
            LEFT JOIN dbo_AMEDEJEC m ON u.CODIGO = m.USUHC
            WHERE u.APELLIDO = ? AND u.CONTRA = ?
        """
    else:  # sqlserver
        query = """
            SELECT u.CODIGO, u.APELLIDO, u.NIVEL, u.ACTIVO, m.CODMED
            FROM dbo.AUSUARIOS u
            LEFT JOIN dbo.AMEDEJEC m ON u.CODIGO = m.USUHC
            WHERE u.APELLIDO = ? AND u.CONTRA = ?
        """

    cursor.execute(query, (usuario, clave))
    resultado = cursor.fetchone()
    conn.close()

    if resultado and resultado.ACTIVO == 1:
        return {
            "CODIGO": resultado.CODIGO,
            "APELLIDO": resultado.APELLIDO.strip(),
            "NIVEL": resultado.NIVEL,
            "CODMED": resultado.CODMED  #ID del profesional
        }
    else:
        return None
    
def obtener_lista_usuarios():
    conn = obtener_conexion()
    cursor = conn.cursor()

    if MODO_CONEXION == "access":
        query = "SELECT DISTINCT APELLIDO FROM dbo_AUSUARIOS WHERE APELLIDO IS NOT NULL ORDER BY APELLIDO"
    else:
        query = "SELECT DISTINCT u.APELLIDO FROM dbo.AUSUARIOS u WHERE u.APELLIDO IS NOT NULL ORDER BY u.APELLIDO"

    cursor.execute(query)
    resultados = [row[0].strip() for row in cursor.fetchall()]
    conn.close()
    return resultados
