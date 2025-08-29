# -*- coding: utf-8 -*-
"""
Created on Wed May 21 19:17:19 2025

@author: Jonathan
"""
import pyodbc
import acceso_db.config as config

def obtener_conexion():
    try:
        if config.MODO_CONEXION == "access":
            conn_str = (
                r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
                fr"DBQ={config.RUTA_ACCESS};"
                r"ExtendedAnsiSQL=1;"
            )
        else:  # sqlserver
            conn_str = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={config.SQLSERVER_CONFIG['server']};"
                f"DATABASE={config.SQLSERVER_CONFIG['database']};"
                f"UID={config.SQLSERVER_CONFIG['username']};"
                f"PWD={config.SQLSERVER_CONFIG['password']};"
                "Encrypt=yes;"
                f"TrustServerCertificate=yes;"
            )
        return pyodbc.connect(conn_str)
    except pyodbc.Error as e:
        mensaje = "No se pudo conectar a la base de datos.\n"
        if config.MODO_CONEXION == "access":
            mensaje += "Verifique que el archivo de base de datos existe y no está en uso."
        else:
            mensaje += "Verifique que el servidor SQL está encendido y accesible."
        print(f"Error técnico: {e}")
        raise Exception(mensaje)