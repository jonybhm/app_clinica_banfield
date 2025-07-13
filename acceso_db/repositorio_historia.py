# -*- coding: utf-8 -*-
"""
Created on Wed May 21 19:20:39 2025

@author: Jonathan
"""
from acceso_db.conexion import obtener_conexion
from acceso_db.config import MODO_CONEXION
from datetime import datetime

def buscar_turnos(fecha, estado, id_profesional, nombre_profesional):
    conn = obtener_conexion()
    cursor = conn.cursor()
    parametros = [fecha, id_profesional]

    if MODO_CONEXION == "access":
        query = """
            SELECT 
                t.CODPAC, t.HORATUR, t.MINTUR, t.HORAREC, t.FECHTUR,
                p.NOMBRE, p.FENAC, p.SEXO,
                h.EVOLUCION
            FROM 
                ((dbo_AMOVTURN AS t
                LEFT JOIN dbo_AHISTORPAC AS p ON t.CODPAC = p.CODPAC)
                LEFT JOIN dbo_AHISTCLIN AS h ON (h.CODPAC = t.CODPAC AND h.FECHA = t.FECHTUR AND h.PROFES = t.CODIGO))
            WHERE 
                FORMAT(t.FECHTUR, 'yyyy-mm-dd') = ? AND t.CODIGO = ?
        """

    else:
        query = """
            SELECT 
                t.CODPAC, t.HORATUR, t.MINTUR, t.HORAREC, t.FECHTUR,
                p.NOMBRE, p.FENAC, p.SEXO,
                h.EVOLUCION
            FROM dbo_AMOVTURN t
            LEFT JOIN dbo_AHISTORPAC p ON t.CODPAC = p.CODPAC
            LEFT JOIN dbo_AHISTCLIN h ON h.CODPAC = t.CODPAC AND h.FECHA = t.FECHTUR AND h.PROFES = t.CODIGO
            WHERE CONVERT(date, t.FECHTUR) = ? AND t.CODIGO = ?
        """

    if estado == "PENDIENTE":
        query += " AND (h.EVOLUCION IS NULL OR LEN(h.EVOLUCION) < 10)"
    elif estado == "ATENDIDO":
        query += " AND h.EVOLUCION IS NOT NULL AND LEN(h.EVOLUCION) >= 10"

    query += " ORDER BY t.HORATUR, t.MINTUR"

    cursor.execute(query, parametros)
    resultados = cursor.fetchall()
    conn.close()

    datos = []
    for row in resultados:
        codpac, horatur, mintur, horarec, fecha, nombre, fenac, sexo, evolucion = row

        edad = calcular_edad(fenac)
        hora_turno = horatur * 100 + mintur if horatur is not None and mintur is not None else None
        espera = calcular_espera(horarec, hora_turno)
        sexo_txt = "FEMENINO" if sexo == 2 else "MASCULINO" if sexo == 1 else "-"
        
        datos.append((
            nombre,
            f"{edad} años" if edad else "?",
            sexo_txt,
            format_hora(horarec),
            espera,
            format_hora(hora_turno),
            nombre_profesional  # ← ahora sí muestra el médico
        ))

    return datos

def calcular_edad(fecha_nacimiento):
    if not fecha_nacimiento or not isinstance(fecha_nacimiento, datetime):
        return None
    hoy = datetime.today()
    return hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

def format_hora(valor):
    if isinstance(valor, int):  # HHMM
        h = valor // 100
        m = valor % 100
        return f"{h:02}:{m:02}"
    if isinstance(valor, datetime):
        return valor.strftime("%H:%M")
    if isinstance(valor, str) and ":" in valor:
        try:
            hora = datetime.strptime(valor, "%d/%m/%Y %H:%M:%S")
            return hora.strftime("%H:%M")
        except:
            return valor[:5]
    return "-"

def calcular_espera(hora_recep, hora_turno):
    if not hora_recep or not hora_turno:
        return "-"
    try:
        h_turno = hora_turno // 100
        m_turno = hora_turno % 100
        t_turno = h_turno * 60 + m_turno

        h_recep, m_recep = map(int, str(hora_recep).split(":")[:2])
        t_recep = h_recep * 60 + m_recep
        dif = t_recep - t_turno
        return f"{dif}:{abs(dif % 60):02}"
    except:
        return "-"