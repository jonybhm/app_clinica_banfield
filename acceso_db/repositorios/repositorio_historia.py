# -*- coding: utf-8 -*-
"""
Created on Wed May 21 19:20:39 2025

@author: Jonathan
"""

#acceso_db/repositorio_historia.py
from acceso_db.conexion import obtener_conexion
from acceso_db.config import MODO_CONEXION
from datetime import datetime


def buscar_turnos(fecha, estado, id_profesional, nombre_profesional):
    conn = obtener_conexion()
    cursor = conn.cursor()

    # Obtener turnos y datos de ACABPAC
    cursor.execute("""
        SELECT 
            COALESCE(t.CODPAC, c.CODPAC) AS CODPAC,
            COALESCE(t.FECHTUR, c.FEPACIENTE) AS FECHA,
            t.HORATUR, t.MINTUR,
            p.NOMBRE, p.FENAC, p.SEXO, p.HISTORIACLI,
            c.RECEPCION, c.HORA AS HORAREC, c.ANULADO, c.ATENDHC
        FROM dbo.AMOVTURN t
        FULL OUTER JOIN dbo.ACABPAC c 
            ON c.CODPAC = t.CODPAC
            AND CAST(c.FEPACIENTE AS DATE) = CAST(t.FECHTUR AS DATE)
            AND c.MEDEJEPAC = t.CODIGO
        LEFT JOIN dbo.AHISTORPAC p 
            ON COALESCE(t.CODPAC, c.CODPAC) = p.CODPAC
        WHERE CAST(COALESCE(t.FECHTUR, c.FEPACIENTE) AS DATE) = CAST(? AS DATE)
          AND COALESCE(t.CODIGO, c.MEDEJEPAC) = ?
    """, (fecha, id_profesional))

    resultados = cursor.fetchall()
    conn.close()

    datos = []
    for row in resultados:
        (codpac, fecha_tur, horatur, mintur,
         nombre, fenac, sexo, hclin,
         recepcion, horarec, anulado, atendhc) = row

        if not codpac or not nombre:
            continue

        edad = calcular_edad(fenac)
        hora_turno_fmt = format_hora(horatur * 100 + mintur if horatur is not None else None)
        hora_recep_fmt = format_hora(horarec)

        # Estado de recepción
        if anulado == 1:
            recepcion_txt = "🚫 TURNO ANULADO"
        elif not hclin or hclin == 0:
            recepcion_txt = "⚠️ FALTA HC"
        elif recepcion:
            recepcion_txt = f"✔️ {hora_recep_fmt}"
        else:
            recepcion_txt = "❌ NO RECEPCION."

        sexo_txt = "FEMENINO" if sexo == 2 else "MASCULINO" if sexo == 1 else "-"

        datos.append({
            "CODPAC": codpac,
            "NOMBRE": nombre,
            "EDAD": f"{edad} años" if edad else "?",
            "SEXO": sexo_txt,
            "FECHA": fecha_tur,
            "HORA": hora_turno_fmt,
            "HORAREC": hora_recep_fmt,
            "RECEPCION": recepcion_txt,
            "HCLIN": hclin,
            "ANULADO": anulado,
            "ATENDHC": atendhc or 0,
            "PROFESIONAL": nombre_profesional,
            "ID_PROFESIONAL": id_profesional
        })


    return datos





def calcular_edad(fecha_nacimiento):
    if not fecha_nacimiento or not isinstance(fecha_nacimiento, datetime):
        return None
    hoy = datetime.today()
    return hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

def format_hora(valor):
    if isinstance(valor, int):
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
    
def agregar_evolucion(codpac, hclin, profes, evolucion_texto, fecha=None, hora=None):
    conn = obtener_conexion()
    cursor = conn.cursor()

    if not fecha:
        fecha = datetime.today().date()
    if not hora:
        hora = datetime.now().time().strftime("%H:%M:%S")

    # Obtener próximo SECUEN
    if MODO_CONEXION == "access":
        cursor.execute("""
            SELECT MAX(SECUEN) FROM dbo_AHISTCLIN
            WHERE CODPAC = ? AND FECHA = ?
        """, (codpac, fecha))
    else:
        cursor.execute("""
            SELECT MAX(SECUEN) FROM dbo.AHISTCLIN
            WHERE CODPAC = ? AND FECHA = ?
        """, (codpac, fecha))
    resultado = cursor.fetchone()
    secuen = (resultado[0] or 0) + 1

    # Obtener próximo PROTOCOLO
    if MODO_CONEXION == "access":
        cursor.execute("SELECT MAX(PROTOCOLO) FROM dbo_AHISTCLIN")
    else:
        cursor.execute("SELECT MAX(PROTOCOLO) FROM dbo.AHISTCLIN")

    resultado = cursor.fetchone()
    protocolo = (resultado[0] or 1000000) + 1

    if MODO_CONEXION == "access":
        query = """
            INSERT INTO dbo_AHISTCLIN (HCLIN, FECHA, SECUEN, PROFES, CODPAC, EVOLUCION, HORA, PROTOCOLO)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
    else:
        query = """
            INSERT INTO dbo.AHISTCLIN (HCLIN, FECHA, SECUEN, PROFES, CODPAC, EVOLUCION, HORA, PROTOCOLO)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
    cursor.execute(query, (
        hclin, fecha, secuen, profes, codpac,
        evolucion_texto, hora, protocolo
    ))
    conn.commit()
    conn.close()
    
def obtener_datos_paciente_y_historial(codpac, id_profesional):
    conn = obtener_conexion()
    cursor = conn.cursor()

    # Traer datos del paciente con JOIN a la tabla de obras sociales
    cursor.execute("""
        SELECT 
            p.CODPAC,
            p.HISTORIACLI,
            p.NOMBRE,
            p.FENAC,
            p.SEXO,
            o.DESOBRA AS ENTIDAD_NOMBRE,
            p.COPLAN,
            p.AFILIADO
        FROM dbo.AHISTORPAC p
        LEFT JOIN dbo.AOBRASPX o ON p.ENTIDAD = o.CODOBRA
        WHERE p.CODPAC = ?
    """, (codpac,))
    paciente = cursor.fetchone()

    if not paciente:
        conn.close()
        return None, []

    codpac, hclin, nombre, fenac, sexo, entidad_nombre, coplan, afiliado = paciente

    datos_paciente = {
        "CODPAC": codpac,
        "HCLIN": hclin,
        "NOMBRE": nombre,
        "EDAD": calcular_edad(fenac),
        "SEXO": "FEMENINO" if sexo == 2 else "MASCULINO" if sexo == 1 else "-",
        "ENTIDAD": entidad_nombre or "",
        "PLAN": coplan or "",
        "AFILIADO": afiliado or "",
        "ID_PROFESIONAL": id_profesional
    }

    # Historial clínico con profesional, hora y protocolo
    cursor.execute("""
        SELECT h.FECHA, h.EVOLUCION, m.NOMBRE AS PROFESIONAL, h.HORA, h.PROTOCOLO
        FROM dbo.AHISTCLIN h
        LEFT JOIN dbo.AMEDEJEC m ON h.PROFES = m.CODMED
        WHERE h.CODPAC = ?
        ORDER BY h.FECHA DESC, h.HORA DESC
    """, (codpac,))
    rows = cursor.fetchall()
    conn.close()

    historial = []
    for row in rows:
        historial.append({
            "FECHA": row.FECHA.strftime("%d/%m/%Y") if row.FECHA else "",
            "EVOLUCION": row.EVOLUCION or "",
            "PROFESIONAL": row.PROFESIONAL or "",
            "HORA": row.HORA.strftime("%H:%M:%S") if row.HORA else "",
            "PROTOCOLO": row.PROTOCOLO or ""
        })

    return datos_paciente, historial



def obtener_lista_diagnosticos():
    conn = obtener_conexion()
    cursor = conn.cursor()
    if MODO_CONEXION == "access":
        cursor.execute("SELECT CODIGO, DESCRIPCION FROM dbo_ADIAGPRES ORDER BY DESCRIPCION")
    else:
        cursor.execute("SELECT CODIGO, DESCRIPCION FROM dbo.ADIAGPRES ORDER BY DESCRIPCION")
    resultados = cursor.fetchall()
    conn.close()

    return [(row.CODIGO, row.DESCRIPCION.strip()) for row in resultados]


def obtener_lista_motivos_consulta():
    conn = obtener_conexion()
    cursor = conn.cursor()
    if MODO_CONEXION == "access":
        cursor.execute("SELECT CODIGO, DESCRIPCION FROM dbo_AMOTCONS ORDER BY DESCRIPCION")
    else:
        cursor.execute("SELECT CODIGO, DESCRIPCION FROM dbo.AMOTCONS ORDER BY DESCRIPCION")
    resultados = cursor.fetchall()
    conn.close()

    return [(row.CODIGO, row.DESCRIPCION.strip()) for row in resultados]

def obtener_lista_examenes_complementarios():
    conn = obtener_conexion()
    cursor = conn.cursor()
    if MODO_CONEXION == "access":
        cursor.execute("SELECT CODIGO, DESCRIPCION FROM dbo_AEXCOM ORDER BY DESCRIPCION")
    else:
        cursor.execute("SELECT CODIGO, DESCRIPCION FROM dbo.AEXCOM ORDER BY DESCRIPCION")
    resultados = cursor.fetchall()
    conn.close()

    return [(row.CODIGO, row.DESCRIPCION.strip()) for row in resultados]

def obtener_lista_tratamientos():
    conn = obtener_conexion()
    cursor = conn.cursor()
    if MODO_CONEXION == "access":
        cursor.execute("SELECT CODIGO, DESCRIPCION FROM dbo_ATRATAM ORDER BY DESCRIPCION")
    else:
        cursor.execute("SELECT CODIGO, DESCRIPCION FROM dbo.ATRATAM ORDER BY DESCRIPCION")
    resultados = cursor.fetchall()
    conn.close()

    return [(row.CODIGO, row.DESCRIPCION.strip()) for row in resultados]

def obtener_lista_derivaciones():
    conn = obtener_conexion()
    cursor = conn.cursor()
    if MODO_CONEXION == "access":
        cursor.execute("SELECT CODIGO, DESCRIPCION FROM dbo_ADERIV ORDER BY DESCRIPCION")
    else:
        cursor.execute("SELECT CODIGO, DESCRIPCION FROM dbo.ADERIV ORDER BY DESCRIPCION")
    resultados = cursor.fetchall()
    conn.close()

    return [(row.CODIGO, row.DESCRIPCION.strip()) for row in resultados]

def obtener_pacientes():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT CODPAC, NOMBRE, DOCUMENTO
        FROM dbo.AHISTORPAC
        ORDER BY NOMBRE
        ''')
    filas = cursor.fetchall()
    conn.close()
    return [{"CODPAC": f.CODPAC, "NOMBRE": f.NOMBRE, "DOCUMENTO": f.DOCUMENTO} for f in filas]

def buscar_pacientes(nombre=None, dni=None):
    conn = obtener_conexion()
    cursor = conn.cursor()

    query = """
        SELECT TOP 50 p.CODPAC, p.NOMBRE, p.DOCUMENTO,
               (SELECT TOP 1 EVOLUCION 
                FROM dbo.AHISTCLIN h 
                WHERE h.CODPAC = p.CODPAC 
                ORDER BY FECHA DESC, HORA DESC) AS EVOLUCION
        FROM dbo.AHISTORPAC p
        WHERE 1=1
    """
    params = []
    if dni and dni.strip():
        query += " AND p.DOCUMENTO = ?"
        params.append(dni)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    cols = [col[0] for col in cursor.description]
    conn.close()
    return [dict(zip(cols, row)) for row in rows]

def marcar_turno_atendido(codpac, id_profesional, fecha):
    """Marca un turno como atendido y registra hora de recepción si no estaba"""
    conn = obtener_conexion()
    cursor = conn.cursor()

    hora_sistema = datetime.now().strftime("%H:%M:%S")

    query = """
        UPDATE dbo.AMOVTURN
        SET ATENDIDO = 1,
            HORAREC = ISNULL(HORAREC, ?)
        WHERE CODPAC = ? AND CODIGO = ? AND CONVERT(date, FECHTUR) = ?
    """
    cursor.execute(query, (hora_sistema, codpac, id_profesional, fecha))
    conn.commit()
    conn.close()


def tiene_turnos_en_fecha(fecha, id_profesional):
    """Devuelve True si el profesional tiene turnos ese día"""
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM dbo.AMOVTURN
        WHERE CONVERT(date, FECHTUR) = ? AND CODIGO = ?
    """, (fecha, id_profesional))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def obtener_dias_con_turnos(id_profesional):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT CONVERT(date, FECHTUR) 
        FROM dbo.AMOVTURN
        WHERE CODIGO = ?
    """, (id_profesional,))
    filas = cursor.fetchall()
    conn.close()
    return [f[0] for f in filas if f[0] is not None]

def marcar_turno_atendido(codpac, fecha, id_profesional):
    conn = obtener_conexion()
    cursor = conn.cursor()

    query = """
        UPDATE dbo.AMOVTURN
        SET ATENDIDO = 1
        WHERE CODPAC = ? AND CONVERT(date, FECHTUR) = ? AND CODIGO = ?
    """
    cursor.execute(query, (codpac, fecha, id_profesional))
    conn.commit()
    conn.close()

def paciente_tiene_evolucion(codpac, fecha_turno):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TOP 1 1
        FROM dbo.AHISTCLIN
        WHERE CODPAC = ? AND CAST(FECHA AS DATE) = CAST(? AS DATE)
    """, (codpac, fecha_turno))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def buscar_pacientes_triple_factor(nombre=None, apellido=None, dni=None):
    conn = obtener_conexion()
    cursor = conn.cursor()

    query = """
        SELECT TOP 50 p.CODPAC, p.NOMBRE, p.DOCUMENTO, p.FENAC,
               (SELECT TOP 1 EVOLUCION 
                FROM dbo.AHISTCLIN h 
                WHERE h.CODPAC = p.CODPAC 
                ORDER BY FECHA DESC, HORA DESC) AS EVOLUCION
        FROM dbo.AHISTORPAC p
        WHERE 1=1
    """

    params = []

    # DNI exacto
    if dni:
        query += " AND p.DOCUMENTO = ?"
        params.append(dni)

    # Búsqueda parcial INSENSIBLE a mayúsculas
    if nombre:
        query += " AND UPPER(p.NOMBRE) LIKE UPPER(?)"
        params.append(f"%{nombre}%")

    if apellido:
        query += " AND UPPER(p.NOMBRE) LIKE UPPER(?)"
        params.append(f"%{apellido}%")

    query += " ORDER BY p.NOMBRE"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    cols = [col[0] for col in cursor.description]
    conn.close()
    return [dict(zip(cols, row)) for row in rows]