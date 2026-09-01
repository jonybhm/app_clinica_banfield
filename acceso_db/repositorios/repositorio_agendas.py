# acceso_db/repositorios/repositorio_agendas.py

from acceso_db.conexion import obtener_conexion


def obtener_agendas(codigo_profesional):
    """
    Obtiene las agendas existentes de un profesional.

    ADATMED.CODIGO corresponde a AMEDEJEC.CODMED.
    """

    conn = obtener_conexion()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                CODIGO,
                SECUEN,
                DIA,
                HORAIN,
                MININ,
                HORAFIN,
                MINFIN,
                FRECUEN,
                CONSULT,
                FVIGIN,
                FVIGFIN,
                CANSOBT,
                TIPO
            FROM dbo.ADATMED
            WHERE CODIGO = ?
            ORDER BY FVIGIN DESC, SECUEN
        """, (codigo_profesional,))

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
            })

        return resultados

    finally:
        conn.close()


def crear_agenda(datos):
    """
    Crea una agenda en ADATMED.

    La asignación de SECUEN y el INSERT se realizan dentro
    de la misma transacción para evitar que dos equipos
    asignen simultáneamente la misma secuencia.

    Devuelve los datos de la agenda incluyendo SECUEN.
    """

    conn = obtener_conexion()
    conn.autocommit = False

    cursor = conn.cursor()

    try:
        # ---------------------------------------------------------
        # IMPORTANTE:
        #
        # La secuencia se obtiene dentro de la misma transacción
        # que realizará el INSERT.
        #
        # SERIALIZABLE + UPDLOCK/HOLDLOCK evita que dos procesos
        # calculen simultáneamente el mismo MAX(SECUEN) + 1
        # para el mismo profesional.
        # ---------------------------------------------------------

        cursor.execute(
            "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
        )

        cursor.execute("""
            SELECT ISNULL(MAX(SECUEN), 0) + 1
            FROM dbo.ADATMED WITH (UPDLOCK, HOLDLOCK)
            WHERE CODIGO = ?
        """, (
            datos["CODIGO"],
        ))

        row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                "No se pudo obtener la siguiente secuencia de agenda."
            )

        secuencia = int(row[0])

        # ---------------------------------------------------------
        # INSERT
        # ---------------------------------------------------------

        cursor.execute("""
            INSERT INTO dbo.ADATMED (
                CODIGO,
                SECUEN,
                DIA,
                HORAIN,
                MININ,
                HORAFIN,
                MINFIN,
                FRECUEN,
                CONSULT,
                FVIGIN,
                FVIGFIN,
                CANSOBT,
                TIPO
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datos["CODIGO"],
            secuencia,
            datos["DIA"],
            datos["HORAIN"],
            datos["MININ"],
            datos["HORAFIN"],
            datos["MINFIN"],
            datos["FRECUEN"],
            datos["CONSULT"],
            datos["FVIGIN"],
            datos["FVIGFIN"],
            datos["CANSOBT"],
            datos["TIPO"],
        ))

        conn.commit()

        # No modificamos el diccionario que recibió el worker.
        resultado = dict(datos)
        resultado["SECUEN"] = secuencia

        return resultado

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def obtener_profesionales_activos():
    """
    Obtiene los profesionales activos disponibles
    para la gestión de agendas.

    CODMED será utilizado como ADATMED.CODIGO.
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
            AND LTRIM(RTRIM(NOMBRE)) <> ''
            ORDER BY NOMBRE
        """)

        filas = cursor.fetchall()

        return [
            {
                "CODIGO": fila.CODMED,
                "NOMBRE": fila.NOMBRE.strip()
            }
            for fila in filas
        ]

    finally:
        conn.close()

def obtener_consultorios():
    """
    Obtiene los consultorios definidos en ACONSULTOR.

    CONSULTORIO es el código que se almacena
    en ADATMED.CONSULT.
    """

    conn = obtener_conexion()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                CONSULTORIO,
                DESCRIPCION,
                PLANTA
            FROM dbo.ACONSULTOR
            ORDER BY CONSULTORIO
        """)

        filas = cursor.fetchall()

        return [
            {
                "CODIGO": fila.CONSULTORIO,
                "DESCRIPCION": (
                    fila.DESCRIPCION.strip()
                    if fila.DESCRIPCION
                    else str(fila.CONSULTORIO)
                ),
                "PLANTA": fila.PLANTA
            }
            for fila in filas
        ]

    finally:
        conn.close()