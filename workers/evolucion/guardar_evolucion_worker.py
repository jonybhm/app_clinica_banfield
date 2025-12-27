from workers.base.base_task import BaseTask
from acceso_db.conexion import obtener_conexion
from datetime import datetime

class GuardarEvolucionWorker(BaseTask):
    def __init__(self, datos_paciente, texto_evolucion):
        self.datos = datos_paciente
        self.texto = texto_evolucion
        super().__init__(self._run)

    def _run(self):
        conn = obtener_conexion()
        cursor = conn.cursor()

        hclin = self.datos["HCLIN"]
        codpac = self.datos["CODPAC"]
        id_profesional = self.datos["ID_PROFESIONAL"]

        cursor.execute("SELECT ISNULL(MAX(SECUEN), 0) FROM dbo.AHISTCLIN WHERE CODPAC = ?", (codpac,))
        secuen = cursor.fetchone()[0] + 1

        cursor.execute("SELECT ISNULL(MAX(PROTOCOLO), 0) FROM dbo.AHISTCLIN")
        protocolo = cursor.fetchone()[0] + 1

        cursor.execute("""
            INSERT INTO dbo.AHISTCLIN 
            (HCLIN, FECHA, SECUEN, PROFES, EVOLUCION, HORA, PROTOCOLO, CODPAC)
            VALUES (?, GETDATE(), ?, ?, ?, CONVERT(VARCHAR(5), GETDATE(), 108), ?, ?)
        """, (
            hclin,
            secuen,
            id_profesional,
            self.texto,
            protocolo,
            codpac
        ))

        cursor.execute("""
            UPDATE dbo.ACABPAC
            SET ATENDHC = 1
            WHERE CODPAC = ? AND CAST(FEPACIENTE AS DATE) = CAST(GETDATE() AS DATE)
        """, (codpac,))

        conn.commit()
        conn.close()

        return True
