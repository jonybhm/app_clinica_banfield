# acceso_db/migraciones.py

import logging

from acceso_db.conexion import obtener_conexion


def aplicar_migraciones():
    """
    Aplica las modificaciones propias de la aplicación
    que todavía no existan en la base de datos.

    No modifica tablas legacy.
    """

    logging.info("Verificando migraciones de base de datos...")

    conn = obtener_conexion()
    cursor = conn.cursor()

    try:

        # =====================================================
        # MIGRACIÓN 001
        # SIGNOS CARDIOVASCULARES
        # =====================================================

        cursor.execute("""
            IF OBJECT_ID('dbo.APP_SIGNOS_CARDIO', 'U') IS NULL
            BEGIN

                CREATE TABLE dbo.APP_SIGNOS_CARDIO
                (
                    ID BIGINT IDENTITY(1,1) NOT NULL
                        CONSTRAINT PK_APP_SIGNOS_CARDIO
                        PRIMARY KEY,

                    CODPAC INT NOT NULL,

                    FECHA_HORA DATETIME2(0) NOT NULL
                        CONSTRAINT DF_APP_SIGNOS_CARDIO_FECHA
                        DEFAULT SYSDATETIME(),

                    FC SMALLINT NOT NULL,

                    PAS SMALLINT NOT NULL,

                    PAD SMALLINT NOT NULL,

                    CODMED INT NULL,

                    SECUEN_TURNO BIGINT NULL
                );

                CREATE INDEX IX_APP_SIGNOS_CARDIO_PACIENTE_FECHA
                    ON dbo.APP_SIGNOS_CARDIO
                    (
                        CODPAC,
                        FECHA_HORA
                    );

            END;
        """)

        conn.commit()

        logging.info(
            "Migración 001 verificada/aplicada correctamente."
        )

    except Exception:

        conn.rollback()

        logging.exception(
            "Error aplicando migraciones de base de datos"
        )

        raise

    finally:

        conn.close()