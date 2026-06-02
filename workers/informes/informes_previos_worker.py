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
            SELECT 
                i.PROTOCOLO,
                i.FESTUDIO,
                i.TIPEA,
                i.CMEMO,
                p.NOMBRE AS PACIENTE,
                o.DESOBRA AS ENTIDAD,
                ms.NOMBRE AS MEDICO_SOLICITANTE,
                ap.DESCRIPCION AS TIPOPRACTICA

            FROM dbo.AINFOR i

            LEFT JOIN dbo.AHISTORPAC p 
                ON i.CODPAC = p.CODPAC

            LEFT JOIN dbo.AOBRASPX o 
                ON p.ENTIDAD = o.CODOBRA

            LEFT JOIN dbo.ACABPAC c 
                ON i.PROTOCOLO = c.PROTOCOLO

            LEFT JOIN dbo.MEDSOLIC ms 
                ON c.MEDSOLPAC = ms.CODMED

            -- NUEVO: relacion protocolo -> práctica
            LEFT JOIN dbo.ADETPAC d
                ON i.PROTOCOLO = d.PROTOCOLO

            LEFT JOIN dbo.APRACTIC ap
                ON d.PRACTICA = ap.CODIGO

            WHERE i.CODPAC = ?
            ORDER BY i.FESTUDIO DESC
        """, (self.codpac,))

        filas = cursor.fetchall()
        print("📄 Resultados:", filas)

        resultados = []
        for protocolo, festudio, tipe, cmemo, paciente, entidad, medico_solicitante, tipo_practica in filas:
            resultados.append({
                "PROTOCOLO": protocolo,
                "FESTUDIO": festudio,
                "TIPEA": tipe,
                "CMEMO": cmemo,
                "CODPAC": self.codpac,
                "PACIENTE": paciente or "",
                "ENTIDAD": entidad or "",
                "MEDICO_SOLICITANTE": medico_solicitante or "",
                "TIPOPRACTICA": tipo_practica or ""
            })

        conn.close()
        return resultados

