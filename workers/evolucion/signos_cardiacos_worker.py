# workers/evolucion/signos_cardiacos_worker.py

from workers.base.base_task import BaseTask

from acceso_db.repositorios.repositorio_signos_cardiacos import (
    guardar_signos_cardiacos,
    obtener_signos_cardiacos
)


class GuardarSignosCardiacosWorker(BaseTask):

    def __init__(
        self,
        codpac,
        fc,
        pas,
        pad,
        fecha_hora,
        codmed=None,
        secuen_turno=None
    ):

        self.codpac = codpac
        self.fc = fc
        self.pas = pas
        self.pad = pad

        self.fecha_hora = fecha_hora

        self.codmed = codmed
        self.secuen_turno = secuen_turno

        super().__init__(
            self._do_work
        )

    def _do_work(self):

        return guardar_signos_cardiacos(
            codpac=self.codpac,
            fc=self.fc,
            pas=self.pas,
            pad=self.pad,
            fecha_hora=self.fecha_hora,
            codmed=self.codmed,
            secuen_turno=self.secuen_turno
        )

class CargarSignosCardiacosWorker(BaseTask):

    def __init__(self, codpac):

        self.codpac = codpac

        super().__init__(
            self._do_work
        )

    def _do_work(self):

        return obtener_signos_cardiacos(
            self.codpac
        )