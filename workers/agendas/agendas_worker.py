# workers/agendas/agendas_worker.py

from workers.base.base_task import BaseTask

from acceso_db.repositorios.repositorio_agendas import (
    crear_agenda,
    obtener_agendas,
    obtener_profesionales_activos,
    obtener_consultorios,
)


class CrearAgendaWorker(BaseTask):
    """
    Crea una agenda fuera del hilo principal.
    """

    def __init__(self, datos):
        self.datos = datos
        super().__init__(self._do_work)

    def _do_work(self):
        return crear_agenda(self.datos)


class ObtenerAgendasWorker(BaseTask):
    """
    Obtiene las agendas existentes de un profesional.
    """

    def __init__(self, codigo_profesional):
        self.codigo_profesional = codigo_profesional
        super().__init__(self._do_work)

    def _do_work(self):
        return obtener_agendas(
            self.codigo_profesional
        )


class ObtenerProfesionalesWorker(BaseTask):
    """
    Obtiene los profesionales activos de AMEDEJEC.
    """

    def __init__(self):
        super().__init__(self._do_work)

    def _do_work(self):
        return obtener_profesionales_activos()

class ObtenerConsultoriosWorker(BaseTask):
    """
    Obtiene los consultorios disponibles desde ACONSULTOR.
    """

    def __init__(self):
        super().__init__(self._do_work)

    def _do_work(self):
        return obtener_consultorios()