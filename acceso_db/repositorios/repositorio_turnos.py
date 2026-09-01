# acceso_db/repositorios/repositorio_turnos.py

from acceso_db.conexion import obtener_conexion


# =============================================================
# PROFESIONALES
# =============================================================

def obtener_profesionales_para_turnos():
    """
    Devuelve los profesionales activos de AMEDEJEC.

    CODMED es el código utilizado por:
        ADATMED.CODIGO
        AMOVTURN.CODIGO
        ACANTUR.PROFES
    """

    conn = obtener_conexion()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                CODMED,
                NOMBRE
            FROM dbo.AMEDEJEC
            WHERE ACTIVO = 1
              AND NOMBRE IS NOT NULL
            ORDER BY NOMBRE
        """)

        filas = cursor.fetchall()

        return [
            {
                "CODIGO": fila.CODMED,
                "NOMBRE": fila.NOMBRE.strip()
            }
            for fila in filas
            if fila.NOMBRE and fila.NOMBRE.strip()
        ]

    finally:
        conn.close()


# =============================================================
# AGENDA VIGENTE
# =============================================================

def obtener_agendas_para_fecha(codigo_profesional, fecha, codigo_dia):
    """
    Obtiene las filas de ADATMED que se encuentran vigentes
    para un profesional en una fecha determinada.

    codigo_dia:
        1 = Domingo
        2 = Lunes
        3 = Martes
        4 = Miércoles
        5 = Jueves
        6 = Viernes
        7 = Sábado
    """

    conn = obtener_conexion()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                a.CODIGO,
                a.SECUEN,
                a.DIA,
                a.HORAIN,
                a.MININ,
                a.HORAFIN,
                a.MINFIN,
                a.FRECUEN,
                a.CONSULT,
                a.FVIGIN,
                a.FVIGFIN,
                a.CANSOBT,
                a.TIPO,

                c.DESCRIPCION AS CONSULTORIO_DESC,
                c.PLANTA AS CONSULTORIO_PLANTA

            FROM dbo.ADATMED a

            LEFT JOIN dbo.ACONSULTOR c
                ON c.CONSULTORIO = a.CONSULT

            WHERE a.CODIGO = ?
              AND a.DIA = ?
              AND CAST(? AS DATE)
                  BETWEEN CAST(a.FVIGIN AS DATE)
                      AND CAST(a.FVIGFIN AS DATE)

            ORDER BY
                a.HORAIN,
                a.MININ,
                a.SECUEN
        """, (
            codigo_profesional,
            codigo_dia,
            fecha
        ))

        filas = cursor.fetchall()

        resultados = []

        for fila in filas:

            resultados.append({
                "CODIGO": fila.CODIGO,
                "SECUEN": fila.SECUEN,
                "DIA": fila.DIA,

                "HORAIN": fila.HORAIN,
                "MININ": fila.MININ,

                "HORAFIN": fila.HORAFIN,
                "MINFIN": fila.MINFIN,

                "FRECUEN": fila.FRECUEN,

                "CONSULT": fila.CONSULT,

                "FVIGIN": fila.FVIGIN,
                "FVIGFIN": fila.FVIGFIN,

                "CANSOBT": fila.CANSOBT,
                "TIPO": fila.TIPO,

                "CONSULTORIO_DESC":
                    fila.CONSULTORIO_DESC.strip()
                    if fila.CONSULTORIO_DESC
                    else "",

                "CONSULTORIO_PLANTA":
                    fila.CONSULTORIO_PLANTA,
            })

        return resultados

    finally:
        conn.close()


# =============================================================
# TURNOS PROGRAMADOS
# =============================================================

def obtener_turnos_programados(codigo_profesional, fecha):
    """
    Obtiene todos los registros de AMOVTURN del profesional
    para la fecha indicada.

    IMPORTANTE:
    Por ahora NO filtramos CSTUR porque todavía no conocemos
    con certeza su significado.
    """

    conn = obtener_conexion()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                t.CODIGO,
                t.FECHTUR,
                t.HORATUR,
                t.MINTUR,
                t.SECUEN,
                t.PRACTICA,
                t.OBSER,
                t.OCULIBRE,
                t.RECEPCION,
                t.CODPAC,
                t.LOCKEO,
                t.CSTUR,
                t.ATENDIDO,
                t.HORAMIN,
                t.DIA,
                t.CONFIRMADO,

                p.NOMBRE AS PACIENTE,
                p.DOCUMENTO

            FROM dbo.AMOVTURN t

            LEFT JOIN dbo.AHISTORPAC p
                ON p.CODPAC = t.CODPAC

            WHERE t.CODIGO = ?
              AND CAST(t.FECHTUR AS DATE) = CAST(? AS DATE)

            ORDER BY
                t.HORATUR,
                t.MINTUR,
                t.SECUEN
        """, (
            codigo_profesional,
            fecha
        ))

        filas = cursor.fetchall()

        resultados = []

        for fila in filas:

            resultados.append({
                "CODIGO": fila.CODIGO,
                "FECHTUR": fila.FECHTUR,

                "HORATUR": fila.HORATUR,
                "MINTUR": fila.MINTUR,

                "SECUEN": fila.SECUEN,
                "PRACTICA": fila.PRACTICA,

                "OBSER":
                    fila.OBSER.strip()
                    if fila.OBSER
                    else "",

                "OCULIBRE": fila.OCULIBRE,
                "RECEPCION": fila.RECEPCION,

                "CODPAC": fila.CODPAC,

                "LOCKEO":
                    fila.LOCKEO.strip()
                    if isinstance(fila.LOCKEO, str)
                    else fila.LOCKEO,

                "CSTUR": fila.CSTUR,
                "ATENDIDO": fila.ATENDIDO,
                "HORAMIN": fila.HORAMIN,
                "DIA": fila.DIA,
                "CONFIRMADO": fila.CONFIRMADO,

                "PACIENTE":
                    fila.PACIENTE.strip()
                    if fila.PACIENTE
                    else "",

                "DOCUMENTO": fila.DOCUMENTO,
            })

        return resultados

    finally:
        conn.close()


# =============================================================
# BLOQUEOS / CANCELACIONES DE AGENDA
# =============================================================

def obtener_bloqueos_para_fecha(codigo_profesional, fecha):
    """
    Obtiene registros de ACANTUR cuyo rango de fechas
    incluye la fecha consultada.

    DIAINI / DIAFIN se interpretarán posteriormente
    en Python.
    """

    conn = obtener_conexion()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                CODIGO,
                FECHA,
                PROFES,
                FEINI,
                FEFIN,

                HORAINI,
                HORAFIN,
                MININI,
                MINFIN,

                MOTIVO,
                USUARIO,

                DIAINI,
                DIAFIN

            FROM dbo.ACANTUR

            WHERE PROFES = ?
              AND CAST(? AS DATE)
                  BETWEEN CAST(FEINI AS DATE)
                      AND CAST(FEFIN AS DATE)

            ORDER BY
                HORAINI,
                MININI,
                CODIGO
        """, (
            codigo_profesional,
            fecha
        ))

        filas = cursor.fetchall()

        resultados = []

        for fila in filas:

            resultados.append({
                "CODIGO": fila.CODIGO,
                "FECHA": fila.FECHA,
                "PROFES": fila.PROFES,

                "FEINI": fila.FEINI,
                "FEFIN": fila.FEFIN,

                "HORAINI": fila.HORAINI,
                "HORAFIN": fila.HORAFIN,

                "MININI": fila.MININI,
                "MINFIN": fila.MINFIN,

                "MOTIVO": fila.MOTIVO,
                "USUARIO": fila.USUARIO,

                "DIAINI": fila.DIAINI,
                "DIAFIN": fila.DIAFIN,
            })

        return resultados

    finally:
        conn.close()