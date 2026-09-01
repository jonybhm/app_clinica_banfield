# modulos/turnos/asignacion_turnos.py

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QDateEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QGroupBox,
)

from PyQt5.QtCore import (
    Qt,
    QDate,
    QSize
)

from PyQt5.QtGui import (
    QIcon,
    QColor,
    QBrush
)

from workers.base.task_manager import (
    TaskManager
)

from workers.turnos.disponibilidad_turnos_worker import (
    ObtenerProfesionalesTurnosWorker,
    DisponibilidadTurnosWorker,
)


class PantallaAsignacionTurnos(QWidget):

    def __init__(self, datos_usuario=None, parent=None):
        super().__init__(parent)

        self.datos_usuario = (
            datos_usuario or {}
        )

        self.resultado_actual = None

        self.setWindowTitle(
            "Asignación de Turnos"
        )

        
        # =====================================================
        # LAYOUT PRINCIPAL
        # =====================================================

        layout = QVBoxLayout(self)

        titulo = QLabel(
            "Disponibilidad y Asignación de Turnos"
        )

        titulo.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
        """)

        layout.addWidget(titulo)

        # =====================================================
        # FILTROS
        # =====================================================

        grupo_filtros = QGroupBox(
            "Buscar disponibilidad"
        )

        filtros = QHBoxLayout()

        # -----------------------------------------------------
        # PROFESIONAL
        # -----------------------------------------------------

        filtros.addWidget(
            QLabel("Profesional:")
        )

        self.profesional_combo = QComboBox()

        self.profesional_combo.setEditable(True)

        self.profesional_combo.setInsertPolicy(
            QComboBox.NoInsert
        )

        self.profesional_combo.setMinimumWidth(
            400
        )

        completer = (
            self.profesional_combo.completer()
        )

        completer.setCaseSensitivity(
            Qt.CaseInsensitive
        )

        completer.setFilterMode(
            Qt.MatchContains
        )

        self.profesional_combo.addItem(
            "Cargando profesionales...",
            None
        )

        self.profesional_combo.setEnabled(
            False
        )

        filtros.addWidget(
            self.profesional_combo
        )

        # -----------------------------------------------------
        # FECHA
        # -----------------------------------------------------

        filtros.addWidget(
            QLabel("Fecha:")
        )

        self.fecha_edit = QDateEdit()

        self.fecha_edit.setCalendarPopup(True)

        self.fecha_edit.setDisplayFormat(
            "dd/MM/yyyy"
        )

        self.fecha_edit.setDate(
            QDate.currentDate()
        )

        filtros.addWidget(
            self.fecha_edit
        )

        # -----------------------------------------------------
        # BUSCAR
        # -----------------------------------------------------

        self.btn_buscar = QPushButton(
            "Buscar disponibilidad"
        )

        self.btn_buscar.setIcon(
            QIcon(":/assets/svg/search.svg")
        )

        self.btn_buscar.setIconSize(
            QSize(20, 20)
        )

        self.btn_buscar.clicked.connect(
            self.buscar_disponibilidad
        )

        self.btn_buscar.setEnabled(False)

        filtros.addWidget(
            self.btn_buscar
        )

        grupo_filtros.setLayout(
            filtros
        )

        layout.addWidget(
            grupo_filtros
        )

        # =====================================================
        # INFORMACIÓN
        # =====================================================

        self.lbl_estado = QLabel(
            "Seleccione un profesional y una fecha."
        )

        self.lbl_estado.setWordWrap(True)

        layout.addWidget(
            self.lbl_estado
        )

        self.lbl_resumen = QLabel("")
        

        self.lbl_resumen.setStyleSheet(
            "font-weight: bold;"
        )

        layout.addWidget(
            self.lbl_resumen
        )

        self.lbl_sobreturnos = QLabel("")

        self.lbl_sobreturnos.setStyleSheet(
            "font-weight: bold;"
        )

        layout.addWidget(self.lbl_sobreturnos)

        # =====================================================
        # TABLA
        # =====================================================

        self.tabla = QTableWidget()

        self.tabla.setColumnCount(6)

        self.tabla.setHorizontalHeaderLabels([
            "Hora",
            "Estado",
            "Paciente",
            "Consultorio",
            "Observaciones",
            "Sobreturnos",
        ])

        self.tabla.setAlternatingRowColors(
            True
        )

        self.tabla.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.tabla.setSelectionMode(
            QTableWidget.SingleSelection
        )

        header = (
            self.tabla.horizontalHeader()
        )

        header.setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout.addWidget(
            self.tabla
        )

        self.tabla.cellDoubleClicked.connect(
                self.accion_sobre_turno
            )             


        

        # =====================================================
        # CARGA INICIAL
        # =====================================================

        self.cargar_profesionales()

    # =========================================================
    # PROFESIONALES
    # =========================================================

    def cargar_profesionales(self):

        self.task_profesionales = (
            ObtenerProfesionalesTurnosWorker()
        )

        self.task_profesionales.signals.finished.connect(
            self._profesionales_cargados
        )

        self.task_profesionales.signals.error.connect(
            self._error_profesionales
        )

        TaskManager.instance().run(
            self.task_profesionales,
            "Cargando profesionales..."
        )

    def _profesionales_cargados(
        self,
        profesionales
    ):

        self.profesional_combo.clear()

        self.profesional_combo.addItem(
            "-- Seleccione un profesional --",
            None
        )

        for profesional in profesionales:

            codigo = profesional["CODIGO"]
            nombre = profesional["NOMBRE"]

            self.profesional_combo.addItem(
                (
                    f"{nombre} "
                    f"(Código: {codigo})"
                ),
                codigo
            )

        self.profesional_combo.setCurrentIndex(
            0
        )

        self.profesional_combo.setEnabled(
            True
        )

        self.btn_buscar.setEnabled(
            True
        )

    def _error_profesionales(
        self,
        error
    ):

        self.profesional_combo.clear()

        self.profesional_combo.addItem(
            "Error al cargar profesionales",
            None
        )

        QMessageBox.critical(
            self,
            "Error",
            (
                "No se pudieron cargar "
                f"los profesionales:\n\n{error}"
            )
        )

    # =========================================================
    # DISPONIBILIDAD
    # =========================================================

    def buscar_disponibilidad(self):

        codigo_profesional = (
            self.profesional_combo.currentData()
        )

        if codigo_profesional is None:

            QMessageBox.warning(
                self,
                "Profesional",
                (
                    "Debe seleccionar "
                    "un profesional."
                )
            )

            return

        fecha = (
            self.fecha_edit
            .date()
            .toPyDate()
        )

        self.btn_buscar.setEnabled(False)

        self.profesional_combo.setEnabled(
            False
        )

        self.fecha_edit.setEnabled(
            False
        )

        self.tabla.setRowCount(0)

        self.lbl_estado.setText(
            "Consultando disponibilidad..."
        )

        self.lbl_resumen.clear()

        self.task_disponibilidad = (
            DisponibilidadTurnosWorker(
                codigo_profesional,
                fecha
            )
        )

        self.task_disponibilidad.signals.finished.connect(
            self._disponibilidad_cargada
        )

        self.task_disponibilidad.signals.error.connect(
            self._error_disponibilidad
        )

        TaskManager.instance().run(
            self.task_disponibilidad,
            "Consultando disponibilidad..."
        )

    def _reactivar_controles(self):

        self.btn_buscar.setEnabled(True)

        self.profesional_combo.setEnabled(
            True
        )

        self.fecha_edit.setEnabled(
            True
        )

    def _disponibilidad_cargada(
        self,
        resultado
    ):

        self._reactivar_controles()

        self.resultado_actual = resultado

        agendas = resultado["AGENDAS"]

        slots = resultado["SLOTS"]

        extras = resultado[
            "TURNOS_FUERA_GRILLA"
        ]

        resumen = resultado["RESUMEN"]

        advertencias = resultado[
            "ADVERTENCIAS"
        ]

        # -----------------------------------------------------
        # ESTADO GENERAL
        # -----------------------------------------------------

        if agendas:

            cantidades = [
                int(a.get("CANSOBT") or 0)
                for a in agendas
            ]

            total_sobreturnos = sum(cantidades)

            self.lbl_sobreturnos.setText(
                f"Sobreturnos permitidos por agenda: {total_sobreturnos}"
            )

        else:

            self.lbl_sobreturnos.setText(
                "Información de sobreturnos no disponible para esta fecha."
            )

        if not agendas:

            if extras:
                self.lbl_estado.setText(
                    (
                        "La agenda correspondiente a esta fecha ya no se "
                        "encuentra vigente. Se muestran únicamente los turnos "
                        "registrados históricamente."
                    )
                )

            else:
                self.lbl_estado.setText(
                    (
                        "No existe una agenda vigente "
                        "para este profesional "
                        "en la fecha seleccionada."
                    )
                )

        else:

            self.lbl_estado.setText(
                (
                    f"Se encontraron "
                    f"{len(agendas)} "
                    "bloque(s) de agenda vigente."
                )
            )

        # -----------------------------------------------------
        # RESUMEN
        # -----------------------------------------------------

        self.lbl_resumen.setText(
            (
                f"Disponibles: {resumen['DISPONIBLES']}   |   "
                f"Ocupados: {resumen['OCUPADOS']}   |   "
                f"Cancelados: {resumen['CANCELADOS']}   |   "
                f"Bloqueados: {resumen['BLOQUEADOS']}"
            )
        )

        # -----------------------------------------------------
        # TABLA
        # -----------------------------------------------------

        filas = slots + extras

        filas.sort(
            key=lambda x: (
                x["MINUTO"],
                x.get("AGENDA_SECUEN") or 999999
            )
        )

        self.tabla.setSortingEnabled(
            False
        )

        self.tabla.setRowCount(
            len(filas)
        )

        for fila_idx, slot in enumerate(filas):

            estado = slot["ESTADO"]

            # ---------------------------------------------------------
            # OBSERVACIONES
            # ---------------------------------------------------------

            observaciones = []

            if slot.get("BLOQUEO"):
                observaciones.append(
                    "Agenda bloqueada"
                )

            if slot.get("ES_HISTORICO"):
                observaciones.append(
                    "Registro histórico"
                )

            if estado == "CANCELADO":
                observaciones.append(
                    "Turno cancelado"
                )

            observacion_texto = " | ".join(
                observaciones
            )

            # ---------------------------------------------------------
            # SOBRETURNOS
            # ---------------------------------------------------------

            sobreturnos = slot.get("CANSOBT")

            if sobreturnos is None:
                sobreturnos = ""

            # ---------------------------------------------------------
            # VALORES VISIBLES
            # ---------------------------------------------------------

            valores = [
                slot["HORA"],
                estado,
                slot["PACIENTES"],
                slot["CONSULTORIO"],
                observacion_texto,
                sobreturnos,
            ]

            # ---------------------------------------------------------
            # COLOR SEGÚN ESTADO
            # ---------------------------------------------------------

            if estado == "DISPONIBLE":

                color_fondo = QColor(
                    198, 239, 206
                )

                color_texto = QColor(
                    0, 80, 20
                )

            elif estado == "OCUPADO":

                color_fondo = QColor(
                    189, 215, 238
                )

                color_texto = QColor(
                    20, 50, 90
                )

            elif estado == "CANCELADO":

                color_fondo = QColor(
                    244, 204, 204
                )

                color_texto = QColor(
                    110, 0, 0
                )

            elif estado == "BLOQUEADO":

                color_fondo = QColor(
                    252, 229, 205
                )

                color_texto = QColor(
                    120, 70, 0
                )

            else:

                color_fondo = QColor(
                    220, 220, 220
                )

                color_texto = QColor(
                    70, 70, 70
                )

            # ---------------------------------------------------------
            # INSERTAR CELDAS
            # ---------------------------------------------------------

            for columna, valor in enumerate(
                valores
            ):

                item = QTableWidgetItem(
                    str(
                        valor
                        if valor is not None
                        else ""
                    )
                )

                item.setFlags(
                    item.flags()
                    & ~Qt.ItemIsEditable
                )

                item.setBackground(
                    QBrush(color_fondo)
                )

                item.setForeground(
                    QBrush(color_texto)
                )

                if columna == 0:

                    item.setData(
                        Qt.UserRole,
                        slot
                    )

                self.tabla.setItem(
                    fila_idx,
                    columna,
                    item
                )

        self.tabla.setSortingEnabled(
            True
        )

        self.tabla.sortItems(
            0,
            Qt.AscendingOrder
        )

        # -----------------------------------------------------
        # ADVERTENCIAS
        # -----------------------------------------------------

        if advertencias:

            QMessageBox.warning(
                self,
                "Advertencias",
                "\n".join(advertencias)
            )

    def _error_disponibilidad(
        self,
        error
    ):

        self._reactivar_controles()

        self.lbl_estado.setText(
            "Ocurrió un error al consultar."
        )

        QMessageBox.critical(
            self,
            "Error",
            (
                "No se pudo obtener "
                f"la disponibilidad:\n\n{error}"
            )
        )

    def accion_sobre_turno(
        self,
        fila,
        columna
    ):

        item = self.tabla.item(
            fila,
            0
        )

        if not item:
            return

        slot = item.data(
            Qt.UserRole
        )

        if not slot:
            return

        estado = slot.get(
            "ESTADO"
        )

        # =====================================================
        # DISPONIBLE
        # =====================================================

        if estado == "DISPONIBLE":

            self.abrir_asignacion(
                slot
            )

            return

        # =====================================================
        # OCUPADO
        # =====================================================

        if estado == "OCUPADO":

            self.mostrar_detalle_turno(
                slot
            )

            return

        # =====================================================
        # CANCELADO
        # =====================================================

        if estado == "CANCELADO":

            self.mostrar_turno_cancelado(
                slot
            )

            return

        # =====================================================
        # BLOQUEADO
        # =====================================================

        if estado == "BLOQUEADO":

            QMessageBox.information(
                self,
                "Horario bloqueado",
                (
                    "Este horario no se encuentra "
                    "disponible para asignar turnos."
                )
            )

    def abrir_asignacion(
        self,
        slot
    ):

        hora = slot.get("HORA")

        QMessageBox.information(
            self,
            "Asignar turno",
            (
                f"Horario seleccionado: {hora}\n\n"
                "PROVISORIO: Aca se abriría la ventana de asignación de turno."
            )
        )

    def mostrar_detalle_turno(
        self,
        slot
    ):

        turnos = slot.get(
            "TURNOS_ACTIVOS",
            []
        )

        if not turnos:
            return

        turno = turnos[0]

        paciente = (
            turno.get("PACIENTE")
            or "Sin identificar"
        )

        documento = (
            turno.get("DOCUMENTO")
            or ""
        )

        hora = slot.get(
            "HORA",
            ""
        )

        observacion = (
            turno.get("OBSER")
            or ""
        )

        secuencia = turno.get(
            "SECUEN"
        )

        texto = (
            f"Paciente: {paciente}\n"
            f"Documento: {documento}\n"
            f"Hora: {hora}\n"
            f"Observaciones: {observacion}\n"
        )

        respuesta = QMessageBox.question(
            self,
            "Detalle del turno",
            (
                f"{texto}\n"
                "¿Desea cancelar este turno?"
            ),
            QMessageBox.Yes
            | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:

            self.solicitar_cancelacion(
                secuencia
            )

    def solicitar_cancelacion(
        self,
        secuencia
    ):

        QMessageBox.information(
            self,
            "Cancelación pendiente",
            (
                "PROVISORIO:\n\n"
                f"Turno interno: {secuencia}\n\n"
                "confirmar si CSTUR = 1 es correcto para cancelar el turno."
            )
        )