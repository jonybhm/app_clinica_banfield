# -*- coding: utf-8 -*-
"""
Created on Wed May 21 19:20:39 2025

@author: Jonathan
"""
from acceso_db.conexion import obtener_conexion
from acceso_db.config import MODO_CONEXION
from datetime import datetime

def buscar_turnos(fecha, estado, id_profesional):
    conn = obtener_conexion()
    cursor = conn.cursor()
    parametros = [fecha, id_profesional]

    if MODO_CONEXION == "access":
        query = """
            SELECT p.NOMBRE, p.FENAC, p.SEXO,
                   c.HORAHC, c.FEPACIENTE, c.RECEPCION, c.ATENDHC,
                   e.NOMBRE AS PROFESIONAL
            FROM [dbo_ACABPAC] AS c, [dbo_AHISTORPAC] AS p, [dbo_AEMPLEAD] AS e
            WHERE c.CODPAC = p.CODPAC
              AND c.MEDSOLPAC = e.CODIGO
              AND FORMAT(c.FEPACIENTE, 'yyyy-mm-dd') = ?
              AND c.MEDSOLPAC = ?
        """
    else:
        query = """
            SELECT p.NOMBRE, p.FENAC, p.SEXO,
                   c.HORAHC, c.FEPACIENTE, c.RECEPCION, c.ATENDHC,
                   e.NOMBRE AS PROFESIONAL
            FROM dbo_ACABPAC c
            JOIN dbo_AHISTORPAC p ON c.CODPAC = p.CODPAC
            JOIN dbo_AEMPLEAD e ON c.MEDSOLPAC = e.CODIGO
            WHERE CONVERT(date, c.FEPACIENTE) = ?
              AND c.MEDSOLPAC = ?
        """

    if estado == "PENDIENTE":
        query += " AND c.RECEPCION IS NOT NULL AND c.ATENDHC = 0"
    elif estado == "ATENDIDO":
        query += " AND c.ATENDHC = 1"

    query += " ORDER BY c.HORAHC"

    cursor.execute(query, parametros)
    resultados = cursor.fetchall()
    conn.close()

    # Procesar datos para tabla
    datos = []
    for row in resultados:
        nombre = row[0]
        fenac = row[1]
        sexo = "FEMENINO" if row[2] == 0 else "MASCULINO"
        hora_turno = row[3]
        hora_recep = row[5] if row[5] is not None else None

        edad = calcular_edad(fenac)
        espera = calcular_espera(hora_recep, hora_turno)

        datos.append((
            nombre,
            f"{edad} años",
            sexo,
            format_hora(hora_recep),
            espera,
            format_hora(hora_turno),
            row[7]  # profesional
        ))

    return datos

def calcular_edad(fecha_nacimiento):
    if not fecha_nacimiento:
        return "?"
    hoy = datetime.today()
    return hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )

def format_hora(valor):
    if isinstance(valor, int):  # campo HORAHC puede venir como entero (ej: 830)
        h = valor // 100
        m = valor % 100
        return f"{h:02}:{m:02}"
    return str(valor) if valor else "-"

def calcular_espera(hora_recep, hora_turno):
    if not hora_recep or not hora_turno or not isinstance(hora_turno, int):
        return "-"
    h_turno = hora_turno // 100
    m_turno = hora_turno % 100
    t_turno = h_turno * 60 + m_turno

    try:
        h_recep = int(str(hora_recep).split(":")[0])
        m_recep = int(str(hora_recep).split(":")[1])
        t_recep = h_recep * 60 + m_recep
        minutos = t_recep - t_turno
        return f"{minutos}:{abs((t_recep - t_turno) % 60):02}"
    except:
        return "-"