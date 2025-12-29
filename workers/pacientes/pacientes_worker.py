# aworkers/pacientes/pacientes_worker.py
from workers.base.base_task import BaseTask
from acceso_db.repositorios.repositorio_historia import buscar_pacientes_triple_factor


class BuscarPacientesWorker(BaseTask):
    def __init__(self, dni, nombre, apellido):
        super().__init__(self.buscar_pacientes_task)
        self.dni = dni
        self.nombre = nombre
        self.apellido = apellido

    def buscar_pacientes_task(self):
        return buscar_pacientes_triple_factor(
            dni=self.dni,
            nombre=self.nombre,
            apellido=self.apellido
        )