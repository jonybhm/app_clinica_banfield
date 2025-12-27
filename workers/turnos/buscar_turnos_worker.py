# auxiliar/workers/buscar_turnos_worker.py
from workers.base.base_task import BaseTask
from acceso_db.repositorio_historia import buscar_turnos, paciente_tiene_evolucion

def _buscar_turnos(fecha, estado, id_profesional, nombre_profesional):
    turnos = buscar_turnos(fecha, estado, id_profesional, nombre_profesional)

    if estado == "PENDIENTE":
        turnos = [
            t for t in turnos
            if "✔️" in t.get("RECEPCION", "")
            and t.get("ATENDHC", 0) == 0
            and t.get("ANULADO", 0) == 0
        ]
    elif estado == "ATENDIDO":
        turnos = [t for t in turnos if t.get("ATENDHC", 0) == 1]

    for t in turnos:
        t["TIENE_EVOLUCION"] = paciente_tiene_evolucion(t.get("CODPAC"), fecha)

    return turnos


class BuscarTurnosWorker(BaseTask):
    def __init__(self, fecha, estado, id_profesional, nombre_profesional):
        super().__init__(
            _buscar_turnos,
            fecha,
            estado,
            id_profesional,
            nombre_profesional
        )
