# auxiliar/workers/pacientes_worker.py
from acceso_db.repositorio_historia import buscar_pacientes_triple_factor

def buscar_pacientes_task(dni, nombre, apellido):
    return buscar_pacientes_triple_factor(
        dni=dni,
        nombre=nombre,
        apellido=apellido
    )