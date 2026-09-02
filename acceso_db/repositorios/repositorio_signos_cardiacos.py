# acceso_db/repositorios/repositorio_signos_cardiacos.py

from acceso_db.conexion import obtener_conexion


def guardar_signos_cardiacos(
    codpac,
    fc,
    pas,
    pad,
    fecha_hora,
    codmed=None,
    secuen_turno=None
):
    """
    Guarda una medición de signos cardiovasculares.

    fecha_hora corresponde al momento real de la medición,
    que puede ser ingresado manualmente por el médico.
    """

    conn = obtener_conexion()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO dbo.APP_SIGNOS_CARDIO
            (
                CODPAC,
                FECHA_HORA,
                FC,
                PAS,
                PAD,
                CODMED,
                SECUEN_TURNO
            )
            OUTPUT INSERTED.ID
            VALUES
            (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
        """, (
            codpac,
            fecha_hora,
            fc,
            pas,
            pad,
            codmed,
            secuen_turno
        ))

        nuevo_id = cursor.fetchone()[0]

        conn.commit()

        return nuevo_id

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()


def obtener_signos_cardiacos(codpac):
    """
    Obtiene el historial cardiovascular del paciente
    ordenado cronológicamente.
    """

    conn = obtener_conexion()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                s.ID,
                s.CODPAC,
                s.FECHA_HORA,
                s.FC,
                s.PAS,
                s.PAD,
                s.CODMED,
                s.SECUEN_TURNO,
                m.NOMBRE AS PROFESIONAL

            FROM dbo.APP_SIGNOS_CARDIO s

            LEFT JOIN dbo.AMEDEJEC m
                ON m.CODMED = s.CODMED

            WHERE s.CODPAC = ?

            ORDER BY
                s.FECHA_HORA ASC,
                s.ID ASC
        """, (
            codpac,
        ))

        filas = cursor.fetchall()

        return [
            {
                "ID": fila.ID,
                "CODPAC": fila.CODPAC,
                "FECHA_HORA": fila.FECHA_HORA,

                "FC": fila.FC,
                "PAS": fila.PAS,
                "PAD": fila.PAD,

                "CODMED": fila.CODMED,
                "SECUEN_TURNO": fila.SECUEN_TURNO,

                "PROFESIONAL":
                    fila.PROFESIONAL.strip()
                    if fila.PROFESIONAL
                    else ""
            }

            for fila in filas
        ]

    finally:

        conn.close()