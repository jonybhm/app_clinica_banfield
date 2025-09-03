import pyodbc
import subprocess
import acceso_db.config as config

def obtener_hora_servidor():
    conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={config.SQLSERVER_CONFIG['server']};"
                f"DATABASE={config.SQLSERVER_CONFIG['database']};"
                f"UID={config.SQLSERVER_CONFIG['username']};"
                f"PWD={config.SQLSERVER_CONFIG['password']};"
                "Encrypt=yes;"
                f"TrustServerCertificate=yes;"
            )
    cur = conn.cursor()
    cur.execute("SELECT GETDATE();")
    row = cur.fetchone()
    conn.close()
    return row[0]  # datetime.datetime

def sincronizar_hora_windows(fecha_hora):
    """
    Sincroniza la fecha y hora de Windows con la recibida del servidor SQL.
    Requiere que el usuario tenga permisos de administrador.
    """
    fecha_str = fecha_hora.strftime("%d-%m-%Y")
    hora_str = fecha_hora.strftime("%H:%M:%S")

    # Cambiar fecha
    subprocess.run(["date", fecha_str], shell=True)
    # Cambiar hora
    subprocess.run(["time", hora_str], shell=True)

# -*- coding: utf-8 -*-