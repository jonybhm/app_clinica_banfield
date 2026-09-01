#modulos/agendas/agendas.py

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QPushButton,
    QComboBox,
    QSpinBox,
    QDateEdit,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QGroupBox
)

from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QIcon

from workers.agendas.agendas_worker import (
    CrearAgendaWorker,
    ObtenerAgendasWorker,
    ObtenerProfesionalesWorker,
    ObtenerConsultoriosWorker
)
from workers.base.task_manager import TaskManager


class PantallaAgendas(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # El profesional ya no depende del usuario logueado.
        # Se seleccionará desde AMEDEJEC.
        self.id_profesional = None
        self.nombre_profesional = ""

        self.setWindowTitle("Creación de Agendas")

        # ---------------------------------------------------------
        # LAYOUT PRINCIPAL
        # ---------------------------------------------------------

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # ---------------------------------------------------------
        # TÍTULO
        # ---------------------------------------------------------

        titulo = QLabel("Creación de Agendas")
        titulo.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
        """)

        self.layout.addWidget(titulo)

        # ---------------------------------------------------------
        # PROFESIONAL
        # ---------------------------------------------------------

        profesional_layout = QHBoxLayout()

        profesional_layout.addWidget(
            QLabel("Profesional:")
        )

        self.profesional_combo = QComboBox()

        self.profesional_combo.setMinimumWidth(400)

        # Mientras se consulta SQL
        self.profesional_combo.addItem(
            "Cargando profesionales...",
            None
        )

        self.profesional_combo.setEnabled(False)

        self.profesional_combo.currentIndexChanged.connect(
            self._profesional_cambiado
        )

        profesional_layout.addWidget(
            self.profesional_combo
        )

        profesional_layout.addStretch()

        self.layout.addLayout(
            profesional_layout
        )

        # ---------------------------------------------------------
        # GRUPO DATOS DE AGENDA
        # ---------------------------------------------------------

        grupo = QGroupBox("Datos de la agenda")
        formulario = QFormLayout()

        # ---------------------------------------------------------
        # DÍA
        # ---------------------------------------------------------

        self.dia_combo = QComboBox()

        self.dias = {
            "Domingo": 1,
            "Lunes": 2,
            "Martes": 3,
            "Miércoles": 4,
            "Jueves": 5,
            "Viernes": 6,
            "Sábado": 7,
        }

        for nombre, codigo in self.dias.items():
            self.dia_combo.addItem(nombre, codigo)

        formulario.addRow("Día:", self.dia_combo)

        # ---------------------------------------------------------
        # HORA INICIO
        # ---------------------------------------------------------

        hora_inicio_layout = QHBoxLayout()

        self.hora_inicio = QSpinBox()
        self.hora_inicio.setRange(0, 23)
        self.hora_inicio.setSuffix(" hs")
        self.hora_inicio.setValue(8)

        self.minuto_inicio = QSpinBox()
        self.minuto_inicio.setRange(0, 59)
        self.minuto_inicio.setSuffix(" min")

        hora_inicio_layout.addWidget(self.hora_inicio)
        hora_inicio_layout.addWidget(self.minuto_inicio)

        formulario.addRow("Inicio:", hora_inicio_layout)

        # ---------------------------------------------------------
        # HORA FIN
        # ---------------------------------------------------------

        hora_fin_layout = QHBoxLayout()

        self.hora_fin = QSpinBox()
        self.hora_fin.setRange(0, 23)
        self.hora_fin.setSuffix(" hs")
        self.hora_fin.setValue(12)

        self.minuto_fin = QSpinBox()
        self.minuto_fin.setRange(0, 59)
        self.minuto_fin.setSuffix(" min")

        hora_fin_layout.addWidget(self.hora_fin)
        hora_fin_layout.addWidget(self.minuto_fin)

        formulario.addRow("Final:", hora_fin_layout)

        # ---------------------------------------------------------
        # FRECUENCIA
        # ---------------------------------------------------------

        self.frecuencia = QSpinBox()
        self.frecuencia.setRange(1, 999)
        self.frecuencia.setValue(15)
        self.frecuencia.setSuffix(" min")

        formulario.addRow("Frecuencia:", self.frecuencia)

        # ---------------------------------------------------------
        # SOBRETURNOS
        # ---------------------------------------------------------

        self.sobreturnos = QSpinBox()
        self.sobreturnos.setRange(0, 999)
        self.sobreturnos.setValue(0)

        formulario.addRow("Sobreturnos:", self.sobreturnos)

        # ---------------------------------------------------------
        # CONSULTORIO
        # ---------------------------------------------------------

        self.consultorio = QComboBox()

        self.consultorio.addItem(
            "Cargando consultorios...",
            None
        )

        self.consultorio.setEnabled(False)

        formulario.addRow(
            "Consultorio:",
            self.consultorio
        )

        # ---------------------------------------------------------
        # FECHA INICIO
        # ---------------------------------------------------------

        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_inicio.setDate(QDate.currentDate())

        formulario.addRow("Fecha inicio:", self.fecha_inicio)

        # ---------------------------------------------------------
        # FECHA FIN
        # ---------------------------------------------------------

        self.fecha_fin = QDateEdit()
        self.fecha_fin.setCalendarPopup(True)

        # Por defecto: un mes después
        self.fecha_fin.setDate(
            QDate.currentDate().addMonths(1)
        )

        formulario.addRow("Fecha fin:", self.fecha_fin)

        # ---------------------------------------------------------
        # TIPO
        # ---------------------------------------------------------

        self.tipo = QComboBox()

        self.tipo.addItem("NORMAL", 1)
        self.tipo.addItem("TEMPORAL", 2)

        formulario.addRow("Tipo:", self.tipo)

        grupo.setLayout(formulario)

        self.layout.addWidget(grupo)

        # ---------------------------------------------------------
        # BOTONES
        # ---------------------------------------------------------

        botones = QHBoxLayout()

        self.btn_guardar = QPushButton("Guardar Agenda")
        self.btn_guardar.setIcon(
            QIcon(":/assets/svg/save.svg")
        )
        self.btn_guardar.setIconSize(QSize(20, 20))

        self.btn_guardar.clicked.connect(
            self.guardar_agenda
        )

        botones.addWidget(self.btn_guardar)

        self.btn_actualizar = QPushButton("Actualizar")
        self.btn_actualizar.setIcon(
            QIcon(":/assets/svg/refresh.svg")
        )
        self.btn_actualizar.setIconSize(QSize(20, 20))

        self.btn_actualizar.clicked.connect(
            self.cargar_agendas
        )

        botones.addWidget(self.btn_actualizar)

        botones.addStretch()

        self.layout.addLayout(botones)

        # ---------------------------------------------------------
        # TABLA DE AGENDAS EXISTENTES
        # ---------------------------------------------------------

        self.layout.addWidget(
            QLabel("Agendas existentes:")
        )

        self.tabla = QTableWidget()

        self.tabla.setColumnCount(10)

        self.tabla.setHorizontalHeaderLabels([
            "Sec.",
            "Día",
            "Inicio",
            "Fin",
            "Frecuencia",
            "Consultorio",
            "Inicio vigencia",
            "Fin vigencia",
            "Sobreturnos",
            "Tipo"
        ])

        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabla.setAlternatingRowColors(True)

        self.layout.addWidget(self.tabla)

        # ---------------------------------------------------------
        # CARGAR DATOS
        # ---------------------------------------------------------

        self.cargar_profesionales()
        self.cargar_consultorios()


    # =============================================================
    # CONSULTORIOS
    # =============================================================

    def cargar_consultorios(self):

        self.task_consultorios = ObtenerConsultoriosWorker()

        self.task_consultorios.signals.finished.connect(
            self._consultorios_cargados
        )

        self.task_consultorios.signals.error.connect(
            self._error_cargando_consultorios
        )

        TaskManager.instance().run(
            self.task_consultorios,
            "Cargando consultorios..."
        )


    def _consultorios_cargados(self, consultorios):

        self.consultorio.clear()

        self.consultorio.addItem(
            "-- Seleccione un consultorio --",
            None
        )

        for consultorio in consultorios:

            codigo = consultorio["CODIGO"]
            descripcion = consultorio["DESCRIPCION"]
            planta = consultorio["PLANTA"]

            texto = (
                f"{descripcion} "
                f"(Planta {planta})"
            )

            self.consultorio.addItem(
                texto,
                codigo
            )

        self.consultorio.setCurrentIndex(0)
        self.consultorio.setEnabled(True)


    def _error_cargando_consultorios(self, error):

        self.consultorio.clear()

        self.consultorio.addItem(
            "Error al cargar consultorios",
            None
        )

        self.consultorio.setEnabled(False)

        QMessageBox.critical(
            self,
            "Error",
            (
                "No se pudo obtener la lista de "
                f"consultorios:\n\n{error}"
            )
        )


    # =============================================================
    # PROFESIONALES
    # =============================================================

    def cargar_profesionales(self):

        self.profesional_combo.setEnabled(False)

        self.task_profesionales = ObtenerProfesionalesWorker()

        self.task_profesionales.signals.finished.connect(
            self._profesionales_cargados
        )

        self.task_profesionales.signals.error.connect(
            self._error_cargando_profesionales
        )

        TaskManager.instance().run(
            self.task_profesionales,
            "Cargando profesionales..."
        )


    def _profesionales_cargados(self, profesionales):

        self.profesional_combo.blockSignals(True)

        self.profesional_combo.clear()

        # No seleccionamos automáticamente al primer médico.
        # Esto evita crear por error una agenda para otra persona.
        self.profesional_combo.addItem(
            "-- Seleccione un profesional --",
            None
        )

        for profesional in profesionales:

            codigo = profesional["CODIGO"]
            nombre = profesional["NOMBRE"]

            self.profesional_combo.addItem(
                f"{nombre} (Código: {codigo})",
                codigo
            )

        self.profesional_combo.setCurrentIndex(0)

        self.profesional_combo.blockSignals(False)

        self.profesional_combo.setEnabled(True)

        self.btn_guardar.setEnabled(False)
        self.btn_actualizar.setEnabled(False)


    def _error_cargando_profesionales(self, error):

        self.profesional_combo.clear()

        self.profesional_combo.addItem(
            "Error al cargar profesionales",
            None
        )

        self.profesional_combo.setEnabled(False)

        QMessageBox.critical(
            self,
            "Error",
            (
                "No se pudo obtener la lista de "
                f"profesionales:\n\n{error}"
            )
        )


    def _profesional_cambiado(self, index):

        codigo = self.profesional_combo.currentData()

        # ----------------------------------------------
        # Ningún profesional seleccionado
        # ----------------------------------------------

        if codigo is None:

            self.id_profesional = None
            self.nombre_profesional = ""

            self.tabla.setRowCount(0)

            self.btn_guardar.setEnabled(False)
            self.btn_actualizar.setEnabled(False)

            return

        # ----------------------------------------------
        # Profesional seleccionado
        # ----------------------------------------------

        self.id_profesional = codigo

        # Obtenemos el nombre visible y quitamos "(Código: xxx)"
        texto = self.profesional_combo.currentText()

        self.nombre_profesional = texto.rsplit(
            " (Código:",
            1
        )[0]

        self.btn_guardar.setEnabled(True)
        self.btn_actualizar.setEnabled(True)

        # Mostrar automáticamente las agendas
        # de ese profesional
        self.cargar_agendas()

    # =============================================================
    # GUARDAR AGENDA
    # =============================================================

    def guardar_agenda(self):

        # ---------------------------------------------------------
        # VALIDAR PROFESIONAL
        # ---------------------------------------------------------

        if not self.id_profesional:
            QMessageBox.warning(
                self,
                "Profesional",
                "Debe seleccionar un profesional."
            )
            return

        # ---------------------------------------------------------
        # VALIDAR FECHAS
        # ---------------------------------------------------------

        fecha_inicio = self.fecha_inicio.date()
        fecha_fin = self.fecha_fin.date()

        if fecha_fin < fecha_inicio:
            QMessageBox.warning(
                self,
                "Datos incorrectos",
                "La fecha de fin no puede ser anterior "
                "a la fecha de inicio."
            )
            return

        # ---------------------------------------------------------
        # VALIDAR HORARIOS
        # ---------------------------------------------------------

        inicio_total = (
            self.hora_inicio.value() * 60
            + self.minuto_inicio.value()
        )

        fin_total = (
            self.hora_fin.value() * 60
            + self.minuto_fin.value()
        )

        if fin_total <= inicio_total:
            QMessageBox.warning(
                self,
                "Datos incorrectos",
                "La hora de finalización debe ser posterior "
                "a la hora de inicio."
            )
            return

        if self.consultorio.currentData() is None:

            QMessageBox.warning(
                self,
                "Consultorio",
                "Debe seleccionar un consultorio."
            )

            return

        # ---------------------------------------------------------
        # DATOS
        # ---------------------------------------------------------
        #
        # SECUEN YA NO SE CALCULA EN LA UI.
        #
        # Lo asignará repositorio_agendas.crear_agenda()
        # dentro de la misma transacción del INSERT.
        # ---------------------------------------------------------

        datos = {
            "CODIGO": self.id_profesional,

            "DIA": self.dia_combo.currentData(),

            "HORAIN": self.hora_inicio.value(),
            "MININ": self.minuto_inicio.value(),

            "HORAFIN": self.hora_fin.value(),
            "MINFIN": self.minuto_fin.value(),

            "FRECUEN": self.frecuencia.value(),

            "CONSULT": self.consultorio.currentData(),

            "FVIGIN": fecha_inicio.toPyDate(),
            "FVIGFIN": fecha_fin.toPyDate(),

            "CANSOBT": self.sobreturnos.value(),

            "TIPO": self.tipo.currentData(),
        }

        # ---------------------------------------------------------
        # CONFIRMACIÓN
        # ---------------------------------------------------------

        confirmacion = QMessageBox.question(
            self,
            "Confirmar agenda",
            (
                f"¿Desea crear esta agenda?\n\n"

                f"Profesional: {self.nombre_profesional}\n"

                f"Día: {self.dia_combo.currentText()}\n"

                f"Horario: "
                f"{self.hora_inicio.value():02d}:"
                f"{self.minuto_inicio.value():02d} - "
                f"{self.hora_fin.value():02d}:"
                f"{self.minuto_fin.value():02d}\n"

                f"Frecuencia: "
                f"{self.frecuencia.value()} minutos\n"

                f"Sobreturnos: "
                f"{self.sobreturnos.value()}\n"

                f"Consultorio: "
                f"{self.consultorio.currentText()}\n"

                f"Vigencia: "
                f"{fecha_inicio.toString('dd/MM/yyyy')} - "
                f"{fecha_fin.toString('dd/MM/yyyy')}\n"

                f"Tipo: {self.tipo.currentText()}"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirmacion != QMessageBox.Yes:
            return

        # ---------------------------------------------------------
        # WORKER
        # ---------------------------------------------------------

        self.btn_guardar.setEnabled(False)
        self.btn_actualizar.setEnabled(False)
        self.profesional_combo.setEnabled(False)

        self.task_crear_agenda = CrearAgendaWorker(
            datos
        )

        self.task_crear_agenda.signals.finished.connect(
            self._agenda_creada
        )

        self.task_crear_agenda.signals.error.connect(
            self._error_creando_agenda
        )

        TaskManager.instance().run(
            self.task_crear_agenda,
            "Creando agenda..."
        )

    # =============================================================
    # AGENDA CREADA
    # =============================================================

    def _agenda_creada(self, datos):

        self.btn_guardar.setEnabled(True)
        self.profesional_combo.setEnabled(True)


        QMessageBox.information(
            self,
            "Agenda creada",
            (
                "La agenda se creó correctamente.\n\n"
                f"Profesional: {self.nombre_profesional}\n"
                f"Día: {self.dia_combo.currentText()}\n"
                f"Secuencia: {datos['SECUEN']}"
            )
        )

        # Refrescamos desde SQL.
        # No suponemos que lo mostrado en pantalla
        # sea el estado real de la tabla.
        self.cargar_agendas()


    def _error_creando_agenda(self, error):

        self.btn_guardar.setEnabled(True)
        self.btn_actualizar.setEnabled(True)
        self.profesional_combo.setEnabled(True)

        QMessageBox.critical(
            self,
            "Error",
            f"No se pudo crear la agenda:\n\n{error}"
        )

    # =============================================================
    # CARGAR AGENDAS
    # =============================================================

    def cargar_agendas(self):

        self.btn_actualizar.setEnabled(False)

        self.tabla.setRowCount(0)

        self.task_cargar_agendas = ObtenerAgendasWorker(
            self.id_profesional
        )

        self.task_cargar_agendas.signals.finished.connect(
            self._agendas_cargadas
        )

        self.task_cargar_agendas.signals.error.connect(
            self._error_cargando_agendas
        )

        TaskManager.instance().run(
            self.task_cargar_agendas,
            "Cargando agendas..."
        )

    def _agendas_cargadas(self, agendas):

        self.btn_actualizar.setEnabled(True)

        nombres_dias = {
            1: "Domingo",
            2: "Lunes",
            3: "Martes",
            4: "Miércoles",
            5: "Jueves",
            6: "Viernes",
            7: "Sábado",
        }

        self.tabla.setRowCount(0)

        for agenda in agendas:

            fila = self.tabla.rowCount()

            self.tabla.insertRow(fila)

            dia = agenda["DIA"]

            nombre_dia = nombres_dias.get(
                dia,
                str(dia)
            )

            hora_inicio = (
                f"{int(agenda['HORAIN'] or 0):02d}:"
                f"{int(agenda['MININ'] or 0):02d}"
            )

            hora_fin = (
                f"{int(agenda['HORAFIN'] or 0):02d}:"
                f"{int(agenda['MINFIN'] or 0):02d}"
            )

            fecha_inicio = agenda["FVIGIN"]

            if fecha_inicio:
                fecha_inicio = fecha_inicio.strftime(
                    "%d/%m/%Y"
                )
            else:
                fecha_inicio = ""

            fecha_fin = agenda["FVIGFIN"]

            if fecha_fin:
                fecha_fin = fecha_fin.strftime(
                    "%d/%m/%Y"
                )
            else:
                fecha_fin = ""

            valores = [
                agenda["SECUEN"],
                nombre_dia,
                hora_inicio,
                hora_fin,
                agenda["FRECUEN"],
                agenda["CONSULT"],
                fecha_inicio,
                fecha_fin,
                agenda["CANSOBT"],
                (
                    "NORMAL"
                    if agenda["TIPO"] == 1
                    else "TIPO 2"
                ),
            ]

            for columna, valor in enumerate(valores):

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

                self.tabla.setItem(
                    fila,
                    columna,
                    item
                )


    def _error_cargando_agendas(self, error):

        self.btn_actualizar.setEnabled(True)

        QMessageBox.critical(
            self,
            "Error",
            f"No se pudieron cargar las agendas:\n\n{error}"
        )