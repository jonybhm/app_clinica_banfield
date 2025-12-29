# workers/pacientes/datos_paciente_worker.py
from workers.base.base_task import BaseTask
from acceso_db.repositorios.repositorio_historia import obtener_datos_paciente_y_historial


class DatosPacienteWorker(BaseTask):
    def __init__(self, codpac, id_profesional):
        super().__init__(self._run)
        self.codpac = codpac
        self.id_profesional = id_profesional

    def _run(self):
        return obtener_datos_paciente_y_historial(
            self.codpac,
            self.id_profesional
        )
