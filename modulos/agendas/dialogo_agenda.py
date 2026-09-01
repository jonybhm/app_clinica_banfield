# modulos/agendas/dialogo_agenda.py

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QSpinBox,
    QDateEdit,
    QMessageBox,
    QFormLayout
)

from workers.base.task_manager import TaskManager
from workers.agendas.agendas_worker import CrearAgendaWorker


class DialogoAgenda(QDialog):

    def __init__(self, profesionales, parent=None):
        super().__init__(parent)

        self.profesionales = profesionales

        self.setWindowTitle("Crear Agenda")
        self.resize(500, 500)

        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Crear nueva agenda")
        titulo.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        layout.addWidget(titulo)

        form = QFormLayout()

        # --------------------------------------------------
        # PROFESIONAL
        # --------------------------------------------------

        self.profesional_combo = QComboBox()

        for profesional in profesionales:
            self.profesional_combo.addItem(
                profesional["NOMBRE"],
                profesional["CODIGO"]
            )

        form.addRow(
            "Profesional:",
            self.profesional_combo
        )

        # --------------------------------------------------
        # DÍA
        # --------------------------------------------------

        self.dia_combo = QComboBox()

        self.dias = [
            ("Domingo", 1),
            ("Lunes", 2),
            ("Martes", 3),
            ("Miércoles", 4),
            ("Jueves", 5),
            ("Viernes", 6),
            ("Sábado", 7),
        ]

        for nombre, codigo in self.dias:
            self.dia_combo.addItem(nombre, codigo)

        # Por defecto Lunes
        indice_lunes = self.dia_combo.findData(2)

        if indice_lunes >= 0:
            self.dia_combo.setCurrentIndex(indice_lunes)

        form.addRow(
            "Día:",
            self.dia_combo
        )

        # --------------------------------------------------
        # HORA INICIO
        # --------------------------------------------------

        self.hora_inicio = QSpinBox()
        self.hora_inicio.setRange(0, 23)
        self.hora_inicio.setSuffix(" h")

        self.min_inicio = QSpinBox()
        self.min_inicio.setRange(0, 59)
        self.min_inicio.setSuffix(" min")

        hora_inicio_layout = QHBoxLayout()
        hora_inicio_layout.addWidget(self.hora_inicio)
        hora_inicio_layout.addWidget(
            QLabel(":")
        )
        hora_inicio_layout.addWidget(self.min_inicio)

        form.addRow(
            "Hora inicio:",
            hora_inicio_layout
        )

        # --------------------------------------------------
        # HORA FIN
        # --------------------------------------------------

        self.hora_fin = QSpinBox()
        self.hora_fin.setRange(0, 23)
        self.hora_fin.setSuffix(" h")

        self.min_fin = QSpinBox()
        self.min_fin.setRange(0, 59)
        self.min_fin.setSuffix(" min")

        hora_fin_layout = QHBoxLayout()
        hora_fin_layout.addWidget(self.hora_fin)
        hora_fin_layout.addWidget(
            QLabel(":")
        )
        hora_fin_layout.addWidget(self.min_fin)

        form.addRow(
            "Hora final:",
            hora_fin_layout
        )

        # --------------------------------------------------
        # FRECUENCIA
        # --------------------------------------------------

        self.frecuencia = QSpinBox()
        self.frecuencia.setRange(1, 999)
        self.frecuencia.setValue(20)
        self.frecuencia.setSuffix(" min")

        form.addRow(
            "Frecuencia:",
            self.frecuencia
        )

        # --------------------------------------------------
        # SOBRETURNOS
        # --------------------------------------------------

        self.sobreturnos = QSpinBox()
        self.sobreturnos.setRange(0, 999)
        self.sobreturnos.setValue(0)

        form.addRow(
            "Sobreturnos:",
            self.sobreturnos
        )

        # --------------------------------------------------
        # CONSULTORIO
        # --------------------------------------------------

        self.consultorio = QComboBox()

        for numero in range(17):
            if numero == 0:
                texto = "0 - Sin especificar"
            else:
                texto = str(numero)

            self.consultorio.addItem(
                texto,
                numero
            )

        form.addRow(
            "Consultorio:",
            self.consultorio
        )

        # --------------------------------------------------
        # FECHA INICIO
        # --------------------------------------------------

        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_inicio.setDisplayFormat("dd/MM/yyyy")

        # Primer día del mes actual
        hoy = QDate.currentDate()

        self.fecha_inicio.setDate(
            QDate(
                hoy.year(),
                hoy.month(),
                1
            )
        )

        form.addRow(
            "Vigencia desde:",
            self.fecha_inicio
        )

        # --------------------------------------------------
        # FECHA FIN
        # --------------------------------------------------

        self.fecha_fin = QDateEdit()
        self.fecha_fin.setCalendarPopup(True)
        self.fecha_fin.setDisplayFormat("dd/MM/yyyy")

        # Último día del mes actual
        ultimo_dia = QDate(
            hoy.year(),
            hoy.month(),
            hoy.daysInMonth()
        )

        self.fecha_fin.setDate(ultimo_dia)

        form.addRow(
            "Vigencia hasta:",
            self.fecha_fin
        )

        # --------------------------------------------------
        # TIPO
        # --------------------------------------------------

        self.tipo = QComboBox()

        self.tipo.addItem(
            "NORMAL",
            1
        )

        self.tipo.addItem(
            "TEMPORAL",
            2
        )

        form.addRow(
            "Tipo:",
            self.tipo
        )

        layout.addLayout(form)

        # --------------------------------------------------
        # BOTONES
        # --------------------------------------------------

        botones = QHBoxLayout()

        self.btn_guardar = QPushButton("Guardar")
        self.btn_cancelar = QPushButton("Cancelar")

        self.btn_guardar.clicked.connect(
            self.guardar
        )

        self.btn_cancelar.clicked.connect(
            self.reject
        )

        botones.addStretch()
        botones.addWidget(self.btn_guardar)
        botones.addWidget(self.btn_cancelar)

        layout.addLayout(botones)

    # ======================================================
    # GUARDAR
    # ======================================================

    def guardar(self):

        fecha_inicio = self.fecha_inicio.date()
        fecha_fin = self.fecha_fin.date()

        if fecha_inicio > fecha_fin:
            QMessageBox.warning(
                self,
                "Datos inválidos",
                "La fecha de inicio no puede ser posterior "
                "a la fecha de finalización."
            )
            return

        # Convertir QDate -> datetime.date
        fecha_inicio_py = fecha_inicio.toPyDate()
        fecha_fin_py = fecha_fin.toPyDate()

        hora_inicio_total = (
            self.hora_inicio.value() * 60
            + self.min_inicio.value()
        )

        hora_fin_total = (
            self.hora_fin.value() * 60
            + self.min_fin.value()
        )

        if hora_inicio_total >= hora_fin_total:
            QMessageBox.warning(
                self,
                "Datos inválidos",
                "La hora de inicio debe ser anterior "
                "a la hora de finalización."
            )
            return

        datos = {
            "CODIGO": self.profesional_combo.currentData(),

            "DIA": self.dia_combo.currentData(),

            "HORAIN": self.hora_inicio.value(),
            "MININ": self.min_inicio.value(),

            "HORAFIN": self.hora_fin.value(),
            "MINFIN": self.min_fin.value(),

            "FRECUEN": self.frecuencia.value(),

            "CONSULT": self.consultorio.currentData(),

            "FVIGIN": fecha_inicio_py,
            "FVIGFIN": fecha_fin_py,

            "CANSOBT": self.sobreturnos.value(),

            "TIPO": self.tipo.currentData()
        }

        self.btn_guardar.setEnabled(False)

        task = CrearAgendaWorker(
            "crear",
            datos=datos
        )

        task.signals.finished.connect(
            self._agenda_creada
        )

        task.signals.error.connect(
            self._error
        )

        TaskManager.instance().run(
            task,
            "Guardando agenda..."
        )

    # ======================================================
    # RESULTADOS
    # ======================================================

    def _agenda_creada(self, secuen):

        QMessageBox.information(
            self,
            "Agenda creada",
            f"La agenda fue creada correctamente.\n\n"
            f"Secuencia asignada: {secuen}"
        )

        self.accept()

    def _error(self, error):

        self.btn_guardar.setEnabled(True)

        QMessageBox.critical(
            self,
            "Error",
            f"No se pudo crear la agenda:\n\n{error}"
        )