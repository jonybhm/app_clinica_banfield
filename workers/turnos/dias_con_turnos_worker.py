from workers.base.base_task import BaseTask
from acceso_db.repositorio_historia import obtener_dias_con_turnos

class DiasConTurnosWorker(BaseTask):
    def __init__(self, id_profesional):
        super().__init__(obtener_dias_con_turnos, id_profesional)
