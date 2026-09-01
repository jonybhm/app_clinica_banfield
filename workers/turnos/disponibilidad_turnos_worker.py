# workers/turnos/disponibilidad_turnos_worker.py

from collections import defaultdict

from workers.base.base_task import BaseTask

from acceso_db.repositorios.repositorio_turnos import (
    obtener_profesionales_para_turnos,
    obtener_agendas_para_fecha,
    obtener_turnos_programados,
    obtener_bloqueos_para_fecha,
)


# =============================================================
# UTILIDADES
# =============================================================

def codigo_dia_legacy(fecha):
    """
    Python:
        Monday = 1
        ...
        Sunday = 7

    Sistema legacy:
        Sunday = 1
        Monday = 2
        ...
        Saturday = 7
    """

    return (fecha.isoweekday() % 7) + 1


def minutos_totales(hora, minuto):
    return int(hora or 0) * 60 + int(minuto or 0)


def formatear_hora(total_minutos):
    hora = total_minutos // 60
    minuto = total_minutos % 60

    return f"{hora:02d}:{minuto:02d}"


def dia_incluido(codigo_dia, dia_inicio, dia_fin):
    """
    Interpretación provisional de DIAINI / DIAFIN de ACANTUR.

    La evidencia actual es compatible con la misma codificación
    utilizada en ADATMED:

        1 Domingo
        2 Lunes
        ...
        7 Sábado

    También contempla un eventual rango que cruce el domingo.
    """

    if dia_inicio is None or dia_fin is None:
        return True

    dia_inicio = int(dia_inicio)
    dia_fin = int(dia_fin)

    if dia_inicio <= dia_fin:
        return dia_inicio <= codigo_dia <= dia_fin

    # Ejemplo hipotético:
    # 6 (viernes) -> 2 (lunes)
    return (
        codigo_dia >= dia_inicio
        or codigo_dia <= dia_fin
    )


def bloqueo_cubre_hora(bloqueo, codigo_dia, minuto_slot):

    if not dia_incluido(
        codigo_dia,
        bloqueo.get("DIAINI"),
        bloqueo.get("DIAFIN")
    ):
        return False

    inicio = minutos_totales(
        bloqueo.get("HORAINI"),
        bloqueo.get("MININI")
    )

    fin = minutos_totales(
        bloqueo.get("HORAFIN"),
        bloqueo.get("MINFIN")
    )

    return inicio <= minuto_slot <= fin


def descripcion_paciente(turno):

    nombre = turno.get("PACIENTE") or ""
    codpac = turno.get("CODPAC")

    if nombre:
        return f"{nombre} [#{codpac}]"

    if codpac:
        return f"Paciente #{codpac}"

    return "Paciente sin identificar"


def descripcion_consultorio(agenda):

    descripcion = agenda.get(
        "CONSULTORIO_DESC"
    )

    codigo = agenda.get("CONSULT")

    planta = agenda.get(
        "CONSULTORIO_PLANTA"
    )

    if not descripcion:
        descripcion = str(codigo or "")

    if planta:
        return (
            f"{descripcion} "
            f"(Planta {planta})"
        )

    return descripcion


# =============================================================
# CÁLCULO DE DISPONIBILIDAD
# =============================================================

def calcular_disponibilidad(codigo_profesional, fecha):

    codigo_dia = codigo_dia_legacy(fecha)

    # ---------------------------------------------------------
    # CONSULTAR BASE
    # ---------------------------------------------------------

    agendas = obtener_agendas_para_fecha(
        codigo_profesional,
        fecha,
        codigo_dia
    )

    turnos = obtener_turnos_programados(
        codigo_profesional,
        fecha
    )

    bloqueos = obtener_bloqueos_para_fecha(
        codigo_profesional,
        fecha
    )

    # ---------------------------------------------------------
    # INDEXAR TURNOS POR HORARIO
    # ---------------------------------------------------------

    turnos_por_hora = defaultdict(list)

    for turno in turnos:

        if turno.get("HORATUR") is None:
            continue

        minuto_turno = minutos_totales(
            turno.get("HORATUR"),
            turno.get("MINTUR")
        )

        turnos_por_hora[minuto_turno].append(
            turno
        )

    # ---------------------------------------------------------
    # GENERAR GRILLA TEÓRICA DESDE ADATMED
    # ---------------------------------------------------------

    slots = []

    horarios_generados = set()

    advertencias = []

    for agenda in agendas:

        frecuencia = int(
            agenda.get("FRECUEN") or 0
        )

        if frecuencia <= 0:

            advertencias.append(
                (
                    f"Agenda {agenda.get('SECUEN')} "
                    "posee una frecuencia inválida."
                )
            )

            continue

        inicio = minutos_totales(
            agenda.get("HORAIN"),
            agenda.get("MININ")
        )

        fin = minutos_totales(
            agenda.get("HORAFIN"),
            agenda.get("MINFIN")
        )

        if fin < inicio:

            advertencias.append(
                (
                    f"Agenda {agenda.get('SECUEN')} "
                    "posee un horario final anterior "
                    "al inicial."
                )
            )

            continue

        minuto_actual = inicio

        # IMPORTANTE:
        # En el ejemplo real 18:30 - 20:30 hay un turno a
        # las 20:30, por eso consideramos HORAFIN inclusivo.

        while minuto_actual <= fin:

            horarios_generados.add(
                minuto_actual
            )

            turnos_slot = turnos_por_hora.get(
                minuto_actual,
                []
            )

            bloqueos_slot = [
                bloqueo
                for bloqueo in bloqueos
                if bloqueo_cubre_hora(
                    bloqueo,
                    codigo_dia,
                    minuto_actual
                )
            ]

            # -------------------------------------------------
            # ESTADO
            # -------------------------------------------------

            # -------------------------------------------------
            # SEPARAR TURNOS ACTIVOS Y CANCELADOS
            # -------------------------------------------------
            #
            # HIPÓTESIS PROVISIONAL:
            # CSTUR = 1  -> turno cancelado
            # CSTUR != 1 -> turno vigente
            #
            # Esto deberá confirmarse contra el sistema XP.
            # -------------------------------------------------

            turnos_cancelados = [
                turno
                for turno in turnos_slot
                if int(turno.get("CSTUR") or 0) == 1
            ]

            turnos_activos = [
                turno
                for turno in turnos_slot
                if int(turno.get("CSTUR") or 0) != 1
            ]

            # -------------------------------------------------
            # ESTADO DEL SLOT
            # -------------------------------------------------

            if bloqueos_slot:
                estado = "BLOQUEADO"

            elif turnos_activos:
                estado = "OCUPADO"

            elif turnos_cancelados:
                estado = "CANCELADO"

            else:
                estado = "DISPONIBLE"

            # -------------------------------------------------
            # PACIENTES
            # -------------------------------------------------

            if turnos_activos:

                pacientes = "; ".join(
                    descripcion_paciente(t)
                    for t in turnos_activos
                )

            elif turnos_cancelados:

                pacientes = "; ".join(
                    descripcion_paciente(t)
                    for t in turnos_cancelados
                )

            else:

                pacientes = ""

            # -------------------------------------------------
            # CSTUR
            # -------------------------------------------------

            valores_cstur = [
                str(t.get("CSTUR"))
                for t in turnos_slot
            ]

            cstur = ", ".join(
                valores_cstur
            )

            # -------------------------------------------------
            # BLOQUEO
            # -------------------------------------------------

            detalle_bloqueo = "; ".join(
                (
                    f"ACANTUR #{b.get('CODIGO')} "
                    f"- Motivo {b.get('MOTIVO')}"
                )
                for b in bloqueos_slot
            )

            slots.append({
                "MINUTO": minuto_actual,

                "HORA": formatear_hora(
                    minuto_actual
                ),

                "ESTADO": estado,

                "CANTIDAD_TURNOS":
                    len(turnos_slot),

                "PACIENTES": pacientes,

                "CONSULTORIO":
                    descripcion_consultorio(
                        agenda
                    ),

                "CONSULTORIO_CODIGO":
                    agenda.get("CONSULT"),

                "AGENDA_SECUEN":
                    agenda.get("SECUEN"),

                "FRECUENCIA":
                    agenda.get("FRECUEN"),

                "CANSOBT":
                    agenda.get("CANSOBT"),

                "BLOQUEO":
                    detalle_bloqueo,

                "CSTUR":
                    cstur,

                "TURNOS":
                    turnos_slot,

                "BLOQUEOS":
                    bloqueos_slot,

                "TURNOS_ACTIVOS": 
                    turnos_activos,
                
                "TURNOS_CANCELADOS": 
                    turnos_cancelados, 
            })

            minuto_actual += frecuencia

    # ---------------------------------------------------------
    # TURNOS FUERA DE LA GRILLA TEÓRICA
    # ---------------------------------------------------------
    #
    # Esto es importante para no ocultar movimientos legacy,
    # sobreturnos o casos que todavía no entendamos.
    # ---------------------------------------------------------

    turnos_fuera_grilla = []

    for minuto_turno, lista_turnos in turnos_por_hora.items():

        if minuto_turno in horarios_generados:
            continue

        pacientes = "; ".join(
            descripcion_paciente(t)
            for t in lista_turnos
        )

        cstur = ", ".join(
            str(t.get("CSTUR"))
            for t in lista_turnos
        )

        activos = [
            t
            for t in lista_turnos
            if int(t.get("CSTUR") or 0) != 1
        ]

        cancelados = [
            t
            for t in lista_turnos
            if int(t.get("CSTUR") or 0) == 1
        ]

        if activos:
            estado_historico = "OCUPADO"

        elif cancelados:
            estado_historico = "CANCELADO"

        else:
            estado_historico = "REGISTRO HISTÓRICO"

        turnos_fuera_grilla.append({
            "MINUTO": minuto_turno,

            "HORA":
                formatear_hora(minuto_turno),

            "ESTADO":
                estado_historico,

            "ES_HISTORICO":
                True,

            "TURNOS_ACTIVOS":
                activos,
                
            "TURNOS_CANCELADOS":
                cancelados,

            "CANTIDAD_TURNOS":
                len(lista_turnos),

            "PACIENTES":
                pacientes,

            "CONSULTORIO":
                "",

            "CONSULTORIO_CODIGO":
                None,

            "AGENDA_SECUEN":
                None,

            "FRECUENCIA":
                None,

            "CANSOBT":
                None,

            "BLOQUEO":
                "",

            "CSTUR":
                cstur,

            "TURNOS":
                lista_turnos,

            "BLOQUEOS":
                [],
        })

    turnos_fuera_grilla.sort(
        key=lambda x: x["MINUTO"]
    )

    slots.sort(
        key=lambda x: (
            x["MINUTO"],
            x["AGENDA_SECUEN"] or 0
        )
    )

    # ---------------------------------------------------------
    # RESUMEN
    # ---------------------------------------------------------

    disponibles = sum(
        1
        for slot in slots
        if slot["ESTADO"] == "DISPONIBLE"
    )

    ocupados = sum(
        1
        for slot in slots
        if slot["ESTADO"] == "OCUPADO"
    )

    cancelados = sum(
        1
        for slot in slots
        if slot["ESTADO"] == "CANCELADO"
    )

    bloqueados = sum(
        1
        for slot in slots
        if slot["ESTADO"] == "BLOQUEADO"
    )

    return {
        "FECHA": fecha,
        "CODIGO_DIA": codigo_dia,

        "AGENDAS": agendas,
        "TURNOS": turnos,
        "BLOQUEOS": bloqueos,

        "SLOTS": slots,

        "TURNOS_FUERA_GRILLA":
            turnos_fuera_grilla,

        "RESUMEN": {
            "AGENDAS":
                len(agendas),

            "SLOTS":
                len(slots),

            "DISPONIBLES": 
                disponibles,

            "OCUPADOS": 
                ocupados,

            "CANCELADOS": 
                cancelados,

            "BLOQUEADOS": 
                bloqueados,

            "FUERA_GRILLA":
                len(turnos_fuera_grilla),

            "REGISTROS_AMOVTURN":
                len(turnos),
        },

        "ADVERTENCIAS":
            advertencias,
    }


# =============================================================
# WORKERS
# =============================================================

class ObtenerProfesionalesTurnosWorker(BaseTask):

    def __init__(self):
        super().__init__(
            obtener_profesionales_para_turnos
        )


class DisponibilidadTurnosWorker(BaseTask):

    def __init__(
        self,
        codigo_profesional,
        fecha
    ):

        self.codigo_profesional = (
            codigo_profesional
        )

        self.fecha = fecha

        super().__init__(
            self._do_work
        )

    def _do_work(self):

        return calcular_disponibilidad(
            self.codigo_profesional,
            self.fecha
        )