# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 13:42:13 2025

@author: Jonathan
"""


#modulos/dialogo_consulta.py
from PyQt5.QtCore import (
    Qt,
    QSize,
    pyqtSignal,
    QDateTime
)
from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import (
    QDialog,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QTextEdit,
    QMessageBox,
    QScrollArea,
    QGroupBox,
    QFormLayout,
    QSpinBox,
    QApplication,
    QDateTimeEdit,
    QLineEdit
)

from datetime import datetime
import os

from auxiliar.editor_texto.rtf_utiles import limpiar_evolucion

from acceso_db.repositorios.repositorio_historia import (     
    obtener_lista_examenes_complementarios,
    obtener_lista_tratamientos,
    obtener_lista_derivaciones,
    marcar_atencion_completa
)

from auxiliar.widgets.widgets_personalizados import ComboBoxBuscador
from acceso_db.conexion import obtener_conexion
from auxiliar.pdf_utiles import generar_pdf_historia

from workers.editor_rtf.abrir_pdf_worker import AbrirPdfWorker
from workers.informes.informes_previos_worker import InformesPreviosWorker

from modulos.informes.dialogo_informes import DialogoInformes
from auxiliar.widgets.spinner import SpinnerDialog

from workers.base.base_task import BaseTask
from workers.base.task_manager import TaskManager

from modulos.informes.dialogo_usar_modelo import DialogoUsarModelo

from workers.evolucion.signos_cardiacos_worker import (
    GuardarSignosCardiacosWorker,
    CargarSignosCardiacosWorker
)

from auxiliar.widgets.grafico_signos_cardiacos import (
    GraficoSignosCardiacos
)

class DialogoConsulta(QDialog):
    evolucion_guardada = pyqtSignal()
    def __init__(self, datos_paciente, historial, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint |
            Qt.WindowCloseButtonHint
        )
        self.setWindowTitle("Nueva Consulta / Ver Historia Clínica")
        self.resize(600, 500)

        self.datos_paciente = datos_paciente  # diccionario
        self.historial = historial            # lista de dicts

        tabs = QTabWidget()
        self.tab_consulta = QWidget()
        self.tab_evolucion = QWidget()

        tabs.addTab(self.tab_consulta, "Consulta")
        tabs.addTab(self.tab_evolucion, "Evolución")

        self._init_tab_consulta()
        self._init_tab_evolucion()

        layout = QVBoxLayout()
        layout.addWidget(tabs)

        # Botones inferiores
        botones_layout = QHBoxLayout()
        boton_guardar = QPushButton("Grabar")
        boton_guardar.clicked.connect(self.confirmar_guardado)
        boton_guardar.setIcon(QIcon(":/assets/svg/save.svg"))
        boton_guardar.setIconSize(QSize(20, 20))

        boton_salir = QPushButton("Salir")
        boton_salir.clicked.connect(self.reject)
        boton_salir.setIcon(QIcon(":/assets/svg/exit.svg"))
        boton_salir.setIconSize(QSize(20, 20))

        boton_imprimir = QPushButton("Imprimir Historial Clínico")
        boton_imprimir.clicked.connect(self.abrir_vista_previa)
        boton_imprimir.setIcon(QIcon(":/assets/svg/print.svg"))
        boton_imprimir.setIconSize(QSize(20, 20))

        boton_informes = QPushButton("Ver Historial de Informes")
        boton_informes.clicked.connect(self.abrir_informes)
        boton_informes.setIcon(QIcon(":/assets/svg/folder.svg"))
        boton_informes.setIconSize(QSize(20, 20))

        boton_informar = QPushButton("Informar Paciente")
        boton_informar.clicked.connect(self.informar_paciente)
        boton_informar.setIcon(QIcon(":/assets/svg/inform.svg"))
        boton_informar.setIconSize(QSize(20, 20))

        botones_layout.addWidget(boton_guardar)
        botones_layout.addWidget(boton_imprimir)
        botones_layout.addWidget(boton_informes)
        botones_layout.addWidget(boton_informar)
        botones_layout.addWidget(boton_salir)

        layout.addLayout(botones_layout)

        self.setLayout(layout)
        self.cargar_signos_cardiacos()
        
        self.setWindowState(Qt.WindowMaximized)

    def _init_tab_consulta(self):

        # =========================================================
        # CONTENIDO PRINCIPAL
        # =========================================================

        contenido = QWidget()
        layout = QVBoxLayout(contenido)

        datos = self.datos_paciente

        # =========================================================
        # DATOS DEL PACIENTE
        # =========================================================

        layout.addWidget(
            QLabel(f"Paciente: {datos['NOMBRE']}")
        )

        layout.addWidget(
            QLabel(f"Fecha: {datos.get('FECHA', '')}")
        )

        layout.addWidget(
            QLabel(
                f"Historia Clínica: {datos.get('HCLIN', '')}"
            )
        )

        layout.addWidget(
            QLabel(f"Hora: {datos.get('HORA', '')}")
        )

        layout.addWidget(
            QLabel(
                f"Protocolo: {datos.get('PROTOCOLO', '')}"
            )
        )

        layout.addWidget(
            QLabel(f"Edad: {datos.get('EDAD', '')}")
        )

        layout.addWidget(
            QLabel(f"Sexo: {datos.get('SEXO', '')}")
        )

        layout.addWidget(
            QLabel(
                f"Entidad: {datos.get('ENTIDAD', '')}   |   "
                f"Plan: {datos.get('PLAN', '')}   |   "
                f"N° Afiliado: {datos.get('AFILIADO', '')}"
            )
        )

        layout.addWidget(
            QLabel(
                f"Profesional: {datos.get('PROFESIONAL', '')}"
            )
        )

        # =========================================================
        # HISTORIAL DEL PACIENTE
        # =========================================================

        titulo_historial = QLabel(
            "Historial del Paciente:"
        )

        titulo_historial.setStyleSheet(
            "font-weight: bold;"
        )

        layout.addWidget(
            titulo_historial
        )

        # =========================================================
        # GRÁFICO CARDIOVASCULAR
        # =========================================================

        grupo_grafico = QGroupBox(
            "Evolución de signos cardiovasculares"
        )

        grafico_layout = QVBoxLayout()

        self.grafico_signos = (
            GraficoSignosCardiacos()
        )

        grafico_layout.addWidget(
            self.grafico_signos
        )

        grupo_grafico.setLayout(
            grafico_layout
        )

        layout.addWidget(
            grupo_grafico
        )

        # =========================================================
        # EVOLUCIONES ANTERIORES
        # =========================================================

        titulo_evoluciones = QLabel(
            "Evoluciones anteriores:"
        )

        titulo_evoluciones.setStyleSheet(
            "font-weight: bold;"
        )

        layout.addWidget(
            titulo_evoluciones
        )

        historial_widget = QWidget()

        historial_layout = QVBoxLayout(
            historial_widget
        )

        for entrada in self.historial:

            fecha = entrada.get(
                "FECHA",
                ""
            )

            evolucion = entrada.get(
                "EVOLUCION",
                ""
            )

            profesional = entrada.get(
                "PROFESIONAL",
                ""
            )

            hora = entrada.get(
                "HORA",
                ""
            )

            protocolo = entrada.get(
                "PROTOCOLO",
                ""
            )

            evolucion_limpia = (
                limpiar_evolucion(
                    evolucion
                )
            )

            lbl_fecha = QLabel(
                str(fecha)
            )

            lbl_fecha.setStyleSheet(
                "font-weight: bold;"
            )

            historial_layout.addWidget(
                lbl_fecha
            )

            texto = QTextEdit()

            texto.setReadOnly(
                True
            )

            texto.setPlainText(
                f"Profesional: {profesional}\n"
                f"Hora: {hora}\n"
                f"Protocolo: {protocolo}\n"
                f"{evolucion_limpia}"
            )

            texto.setFixedHeight(
                120
            )

            historial_layout.addWidget(
                texto
            )

        # No necesitamos un scroll separado
        # para el historial, porque ahora toda
        # la pestaña es scrolleable.

        layout.addWidget(
            historial_widget
        )

        layout.addStretch()

        # =========================================================
        # SCROLL GENERAL DE LA PESTAÑA CONSULTA
        # =========================================================

        scroll_general = QScrollArea()

        scroll_general.setWidgetResizable(
            True
        )

        scroll_general.setWidget(
            contenido
        )

        main_layout = QVBoxLayout(
            self.tab_consulta
        )

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main_layout.addWidget(
            scroll_general
        )

    def _init_tab_evolucion(self):

        layout = QVBoxLayout()

        # =========================================================
        # CAMPOS DE EVOLUCIÓN
        # =========================================================

        # Motivo y diagnóstico ahora son texto libre
        self.txt_motivo = QLineEdit()

        self.txt_motivo.setPlaceholderText(
            "Ingrese el motivo de consulta"
        )

        self.txt_diagnostico = QLineEdit()

        self.txt_diagnostico.setPlaceholderText(
            "Ingrese el diagnóstico"
        )

        # Evolución
        self.txt_evolucion = QTextEdit()

        self.txt_evolucion.setFixedHeight(
            120
        )

        self.txt_evolucion.setPlaceholderText(
            "Ingrese la evolución del paciente"
        )

        # Estos campos continúan usando las opciones existentes
        self.cmb_tratamiento = ComboBoxBuscador()
        self.cmb_examenes = ComboBoxBuscador()
        self.cmb_derivacion = ComboBoxBuscador()

        # =========================================================
        # CARGAR LISTAS DESDE DB
        # =========================================================

        self.examenes = obtener_lista_examenes_complementarios()
        self.tratamientos = obtener_lista_tratamientos()
        self.derivacion = obtener_lista_derivaciones()

        # Convertir en listas con formato "desc (codigo)"

        examenes_items = [""] + [
            f"{desc} ({cod})"
            for cod, desc in self.examenes
        ]
        tratamientos_items = [""] + [
            f"{desc} ({cod})"
            for cod, desc in self.tratamientos
        ]
        derivacion_items = [""] + [
            f"{desc} ({cod})"
            for cod, desc in self.derivacion
        ]

        # Cargar combos


        self.cmb_examenes.setItems(
            examenes_items
        )     
        self.cmb_tratamiento.setItems(
            tratamientos_items
        )
        self.cmb_derivacion.setItems(
            derivacion_items
        )

        # =========================================================
        # MOTIVO
        # =========================================================

        layout.addWidget(
            QLabel("Motivo de Consulta:")
        )

        layout.addWidget(
            self.txt_motivo
        )

        # =========================================================
        # EVOLUCIÓN
        # =========================================================

        layout.addWidget(
            QLabel("Evolución:")
        )

        layout.addWidget(
            self.txt_evolucion
        )

        # =========================================================
        # DIAGNÓSTICO
        # =========================================================

        layout.addWidget(
            QLabel("Diagnóstico:")
        )

        layout.addWidget(
            self.txt_diagnostico
        )

        # =========================================================
        # SIGNOS CARDIOVASCULARES
        # =========================================================

        grupo_signos = QGroupBox(
            "Signos cardiovasculares"
        )

        signos_layout = QVBoxLayout()

        form_signos = QFormLayout()

        # ---------------------------------------------------------
        # FECHA Y HORA
        # ---------------------------------------------------------

        self.fecha_hora_signos = QDateTimeEdit()

        self.fecha_hora_signos.setCalendarPopup(
            True
        )

        self.fecha_hora_signos.setDisplayFormat(
            "dd/MM/yyyy HH:mm"
        )

        # Fecha/hora actual por defecto
        self.fecha_hora_signos.setDateTime(
            QDateTime.currentDateTime()
        )

        form_signos.addRow(
            "Fecha y hora:",
            self.fecha_hora_signos
        )

        # ---------------------------------------------------------
        # FRECUENCIA CARDÍACA
        # ---------------------------------------------------------

        self.spin_fc = QSpinBox()

        self.spin_fc.setRange(
            0,
            300
        )

        self.spin_fc.setSpecialValueText(
            "Sin cargar"
        )

        self.spin_fc.setSuffix(
            " lpm"
        )

        form_signos.addRow(
            "Frecuencia cardíaca:",
            self.spin_fc
        )

        # ---------------------------------------------------------
        # PRESIÓN SISTÓLICA
        # ---------------------------------------------------------

        self.spin_pas = QSpinBox()

        self.spin_pas.setRange(
            0,
            300
        )

        self.spin_pas.setSpecialValueText(
            "Sin cargar"
        )

        self.spin_pas.setSuffix(
            " mmHg"
        )

        form_signos.addRow(
            "Presión sistólica:",
            self.spin_pas
        )

        # ---------------------------------------------------------
        # PRESIÓN DIASTÓLICA
        # ---------------------------------------------------------

        self.spin_pad = QSpinBox()

        self.spin_pad.setRange(
            0,
            200
        )

        self.spin_pad.setSpecialValueText(
            "Sin cargar"
        )

        self.spin_pad.setSuffix(
            " mmHg"
        )

        form_signos.addRow(
            "Presión diastólica:",
            self.spin_pad
        )

        signos_layout.addLayout(
            form_signos
        )

        # ---------------------------------------------------------
        # GUARDAR MEDICIÓN
        # ---------------------------------------------------------

        self.btn_guardar_signos = QPushButton(
            "Guardar medición"
        )

        self.btn_guardar_signos.setIcon(
            QIcon(":/assets/svg/save.svg")
        )

        self.btn_guardar_signos.setIconSize(
            QSize(20, 20)
        )

        self.btn_guardar_signos.clicked.connect(
            self.guardar_signos_cardiacos
        )

        signos_layout.addWidget(
            self.btn_guardar_signos
        )

        nota_signos = QLabel(
            "Las mediciones se guardan con fecha y hora "
            "y quedan asociadas al paciente."
        )

        nota_signos.setWordWrap(
            True
        )

        signos_layout.addWidget(
            nota_signos
        )

        grupo_signos.setLayout(
            signos_layout
        )

        # ACÁ ES DONDE QUEDA INSERTADO:
        # inmediatamente después del diagnóstico
        layout.addWidget(
            grupo_signos
        )

        # =========================================================
        # EXÁMENES COMPLEMENTARIOS
        # =========================================================

        layout.addWidget(
            QLabel("Exámenes Complementarios:")
        )

        layout.addWidget(
            self.cmb_examenes
        )

        # =========================================================
        # TRATAMIENTO
        # =========================================================

        layout.addWidget(
            QLabel("Tratamiento:")
        )

        layout.addWidget(
            self.cmb_tratamiento
        )

        # =========================================================
        # DERIVACIÓN
        # =========================================================

        layout.addWidget(
            QLabel("Derivación:")
        )

        layout.addWidget(
            self.cmb_derivacion
        )

        # =========================================================
        # SCROLL
        # =========================================================

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        container = QWidget()

        container.setLayout(
            layout
        )

        scroll.setWidget(
            container
        )

        main_layout = QVBoxLayout()

        main_layout.addWidget(
            scroll
        )

        self.tab_evolucion.setLayout(
            main_layout
        )

    def guardar_signos_cardiacos(self):

        fc = self.spin_fc.value()
        pas = self.spin_pas.value()
        pad = self.spin_pad.value()

        fecha_hora = (
            self.fecha_hora_signos
            .dateTime()
            .toPyDateTime()
        )

        # ---------------------------------------------------------
        # VALIDACIÓN
        # ---------------------------------------------------------

        if fc == 0:

            QMessageBox.warning(
                self,
                "Signos cardiovasculares",
                "Ingrese la frecuencia cardíaca."
            )

            return

        if pas == 0 or pad == 0:

            QMessageBox.warning(
                self,
                "Signos cardiovasculares",
                (
                    "Ingrese la presión sistólica "
                    "y diastólica."
                )
            )

            return

        if pad >= pas:

            QMessageBox.warning(
                self,
                "Presión arterial",
                (
                    "La presión diastólica debe ser "
                    "menor que la presión sistólica."
                )
            )

            return

        # ---------------------------------------------------------
        # DATOS
        # ---------------------------------------------------------

        codpac = self.datos_paciente[
            "CODPAC"
        ]

        codmed = self.datos_paciente.get(
            "ID_PROFESIONAL"
        )

        secuen_turno = self.datos_paciente.get(
            "SECUEN_TURNO"
        )

        # ---------------------------------------------------------
        # CONFIRMAR
        # ---------------------------------------------------------

        fecha_visible = (
            self.fecha_hora_signos
            .dateTime()
            .toString("dd/MM/yyyy HH:mm")
        )

        respuesta = QMessageBox.question(
            self,
            "Guardar medición",
            (
                "¿Desea guardar esta medición?\n\n"
                f"Fecha y hora: {fecha_visible}\n"
                f"Frecuencia cardíaca: {fc} lpm\n"
                f"Presión arterial: {pas}/{pad} mmHg"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if respuesta != QMessageBox.Yes:
            return

        # ---------------------------------------------------------
        # WORKER
        # ---------------------------------------------------------

        self.btn_guardar_signos.setEnabled(
            False
        )

        self.task_guardar_signos = (
            GuardarSignosCardiacosWorker(
                codpac=codpac,
                fc=fc,
                pas=pas,
                pad=pad,
                fecha_hora=fecha_hora,
                codmed=codmed,
                secuen_turno=secuen_turno
            )
        )

        self.task_guardar_signos.signals.finished.connect(
            self._signos_guardados
        )

        self.task_guardar_signos.signals.error.connect(
            self._error_guardando_signos
        )

        TaskManager.instance().run(
            self.task_guardar_signos,
            "Guardando signos cardiovasculares..."
        )


    def _signos_guardados(self, nuevo_id):

        self.btn_guardar_signos.setEnabled(
            True
        )

        # Limpiar formulario
        self.spin_fc.setValue(0)
        self.spin_pas.setValue(0)
        self.spin_pad.setValue(0)

        QMessageBox.information(
            self,
            "Signos cardiovasculares",
            "La medición se guardó correctamente."
        )

        # Refrescar gráfico
        self.cargar_signos_cardiacos()


    def _error_guardando_signos(
        self,
        error
    ):

        self.btn_guardar_signos.setEnabled(
            True
        )

        QMessageBox.critical(
            self,
            "Error",
            (
                "No se pudo guardar "
                f"la medición:\n\n{error}"
            )
        )


    def cargar_signos_cardiacos(self):

        codpac = self.datos_paciente.get(
            "CODPAC"
        )

        if not codpac:
            return

        self.task_cargar_signos = (
            CargarSignosCardiacosWorker(
                codpac
            )
        )

        self.task_cargar_signos.signals.finished.connect(
            self._signos_cargados
        )

        self.task_cargar_signos.signals.error.connect(
            self._error_cargando_signos
        )

        TaskManager.instance().run(
            self.task_cargar_signos,
            "Cargando signos cardiovasculares..."
        )


    def _signos_cargados(
        self,
        mediciones
    ):

        self.grafico_signos.actualizar(
            mediciones
        )


    def _error_cargando_signos(
        self,
        error
    ):

        QMessageBox.warning(
            self,
            "Signos cardiovasculares",
            (
                "No se pudo cargar "
                f"el historial:\n\n{error}"
            )
        )

    def confirmar_guardado(self):        
        reply = QMessageBox.question(
            self, "Confirmación", "¿Desea guardar esta evolución?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        texto = self.txt_evolucion.toPlainText()

        from workers.evolucion.guardar_evolucion_worker import GuardarEvolucionWorker

        task = GuardarEvolucionWorker(self.datos_paciente, texto)
        task.signals.finished.connect(self._guardar_ok)
        task.signals.error.connect(self._guardar_error)

        TaskManager.instance().run(task, "Guardando evolución...")

    def _guardar_ok(self, _):
        try:
            secuen=self.datos_paciente["SECUEN_TURNO"]                
            print(f"SECUENCIA: {secuen}")
            marcar_atencion_completa(
                secuen=self.datos_paciente.get("SECUEN_TURNO"),
                codpac=self.datos_paciente["CODPAC"],
                fecha=self.datos_paciente.get("FECHA"),
                id_profesional=self.datos_paciente["ID_PROFESIONAL"]
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Aviso",
                f"No se pudo marcar el turno como atendido:\n{e}"
            )

        QMessageBox.information(self, "Éxito", "Evolución guardada correctamente")
        self.evolucion_guardada.emit()
        self.accept()

    def _guardar_error(self, error):
        QMessageBox.critical(self, "Error", str(error))



    def abrir_vista_previa(self):
        task = AbrirPdfWorker(self.datos_paciente, self.historial)
        TaskManager.instance().run(task, "Generando PDF...")


    def abrir_informes(self):
        spinner = SpinnerDialog("Cargando informes...")
        spinner.show()
        QApplication.processEvents()

        codpac = self.datos_paciente["CODPAC"]

        task = InformesPreviosWorker(codpac)
        task.signals.finished.connect(self._mostrar_informes)
        task.signals.error.connect(self._error_informes)

        TaskManager.instance().run(task, "Cargando informes...")

    def _mostrar_informes(self, informes):
        try:
            if not informes:
                QMessageBox.information(self, "Sin informes", "El paciente no tiene informes.")
                return

            dlg = DialogoInformes(
                informes=informes,
                nombre_profesional=self.datos_paciente["PROFESIONAL"],
                parent=self
            )
            dlg.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


    def _error_informes(self, error):
        QMessageBox.critical(self, "Error al cargar informes", error)

    def informar_paciente(self):
        try:
            dlg = DialogoUsarModelo(
                datos_usuario={
                    "CODIGO": self.datos_paciente["ID_PROFESIONAL"],
                    "APELLIDO": self.datos_paciente["PROFESIONAL"],
                },
                parent=self
            )

            nombre = self.datos_paciente["NOMBRE"]
            dni = self.datos_paciente.get("DOCUMENTO", "")
            nombre_visible = f"{nombre} ({dni})"

            dlg.precargar_paciente(
                codpac=self.datos_paciente["CODPAC"],
                nombre_visible=nombre_visible
            )

            dlg.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))