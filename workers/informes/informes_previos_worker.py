# auxiliar/workers/informes_previos_worker.py
from workers.base.base_task import BaseTask
from acceso_db.conexion import obtener_conexion

class InformesPreviosWorker(BaseTask):
    def __init__(self, codpac):
        self.codpac = codpac
        super().__init__(self._do_work)

    def _do_work(self):
        print("🟢 Entrando a InformesPreviosWorker")
        print("CODPAC:", self.codpac)

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT PROTOCOLO, FESTUDIO, TIPEA, CMEMO
            FROM dbo.AINFOR
            WHERE CODPAC = ?
            ORDER BY FESTUDIO DESC
        """, (self.codpac,))

        filas = cursor.fetchall()
        print("📄 Resultados:", filas)

        resultados = []
        for protocolo, festudio, tipe, cmemo in filas:
            resultados.append({
                "PROTOCOLO": protocolo,
                "FESTUDIO": festudio,
                "TIPEA": tipe,
                "CMEMO": cmemo,
                "CODPAC": self.codpac
            })

        conn.close()
        return resultados

