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
            SELECT CODIGO, APELLIDO, NIVEL, ACTIVO
            FROM dbo_AUSUARIOS
            WHERE APELLIDO = ? AND CONTRA = ?
        """
    else:  # sqlserver
        query = """
            SELECT u.CODIGO, u.APELLIDO, u.NIVEL, u.ACTIVO
            FROM dbo_AUSUARIOS u
            WHERE u.APELLIDO = ? AND u.CONTRA = ?
        """

    cursor.execute(query, (usuario, clave))
    resultado = cursor.fetchone()
    conn.close()

    if resultado and resultado.ACTIVO == 1:
        return {
            "CODIGO": resultado.CODIGO,
            "APELLIDO": resultado.APELLIDO.strip(),
            "NIVEL": resultado.NIVEL
        }
    else:
        return None

def obtener_lista_usuarios():
    conn = obtener_conexion()
    cursor = conn.cursor()

    if MODO_CONEXION == "access":
        query = "SELECT DISTINCT APELLIDO FROM dbo_AUSUARIOS WHERE APELLIDO IS NOT NULL ORDER BY APELLIDO"
    else:
        query = "SELECT DISTINCT u.APELLIDO FROM dbo_AUSUARIOS u WHERE u.APELLIDO IS NOT NULL ORDER BY u.APELLIDO"

    cursor.execute(query)
    resultados = [row[0].strip() for row in cursor.fetchall()]
    conn.close()
    return resultados

'''
from acceso_db.conexion import obtener_conexion
from acceso_db.config import MODO_CONEXION

def login_usuario(usuario, clave):
    conn = obtener_conexion()
    cursor = conn.cursor()

    if MODO_CONEXION == "access":
        # Consulta para Access (sin JOIN con alias)
        query = """
            SELECT [dbo_AUSUARIOS].APELLIDO, [dbo_AUSUARIOS].CODIGO AS PROFESIONAL
            FROM [dbo_AUSUARIOS], [dbo_AEMPLEAD]
            WHERE [dbo_AUSUARIOS].APELLIDO = ? AND [dbo_AUSUARIOS].CONTRA = ?
        """
    else:
        # Consulta para SQL Server (con JOIN y alias)
        query = """
            SELECT u.APELLIDO, u.CODIGO AS PROFESIONAL
            FROM dbo_AUSUARIOS u
            WHERE u.APELLIDO = ? AND u.CONTRA = ?
        """

    cursor.execute(query, (usuario, clave))
    resultado = cursor.fetchone()
    conn.close()
    return resultado
'''