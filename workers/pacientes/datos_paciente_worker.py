# auxiliar/workers/datos_paciente_worker.py
from workers.base.base_task import BaseTask
from acceso_db.repositorio_historia import obtener_datos_paciente_y_historial

class DatosPacienteWorker(BaseTask):
    def __init__(self, codpac, id_profesional):
        super().__init__(obtener_datos_paciente_y_historial, codpac, id_profesional)
