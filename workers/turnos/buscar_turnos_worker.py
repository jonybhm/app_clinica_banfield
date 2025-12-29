# auxiliar/workers/buscar_turnos_worker.py
from workers.base.base_task import BaseTask
from acceso_db.repositorios.repositorio_historia import buscar_turnos, paciente_tiene_evolucion

def _buscar_turnos(fecha, estado, id_profesional, nombre_profesional):
    turnos = buscar_turnos(fecha, estado, id_profesional, nombre_profesional)

    resultado = []

    for t in turnos:
        atendido = t.get("ATENDHC", 0) == 1
        anulado = t.get("ANULADO", 0) == 1
        tiene_evo = paciente_tiene_evolucion(t.get("CODPAC"), fecha)

        if estado == "PENDIENTE":
            if not atendido and not tiene_evo and not anulado:
                resultado.append(t)

        elif estado == "ATENDIDO":
            if atendido or tiene_evo:
                resultado.append(t)

        else:  # TODOS
            resultado.append(t)

    # Agregamos flag reutilizable
    for t in resultado:
        t["TIENE_EVOLUCION"] = paciente_tiene_evolucion(t.get("CODPAC"), fecha)

    return resultado



class BuscarTurnosWorker(BaseTask):
    def __init__(self, fecha, estado, id_profesional, nombre_profesional):
        super().__init__(
            _buscar_turnos,
            fecha,
            estado,
            id_profesional,
            nombre_profesional
        )
