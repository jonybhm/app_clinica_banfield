# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 13:42:13 2025

@author: Jonathan
"""


#modulos/dialogo_consulta.py
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QTextEdit, QMessageBox, QScrollArea
)
from datetime import datetime
from auxiliar.editor_texto.rtf_utiles import limpiar_evolucion
from acceso_db.repositorios.repositorio_historia import (
    obtener_lista_diagnosticos,
    obtener_lista_motivos_consulta,
    obtener_lista_examenes_complementarios,
    obtener_lista_tratamientos,
    obtener_lista_derivaciones,
    marcar_turno_atendido
)
from auxiliar.widgets.widgets_personalizados import ComboBoxBuscador
from acceso_db.conexion import obtener_conexion
import os
from auxiliar.pdf_utiles import generar_pdf_historia
from workers.editor_rtf.abrir_pdf_worker import AbrirPdfWorker
from workers.informes.informes_previos_worker import InformesPreviosWorker
from modulos.informes.dialogo_informes import DialogoInformes
from auxiliar.widgets.spinner import SpinnerDialog
from PyQt5.QtWidgets import QApplication
from workers.base.base_task import BaseTask
from workers.base.task_manager import TaskManager
import resources_rc


class DialogoConsulta(QDialog):
    def __init__(self, datos_paciente, historial, parent=None):
        super().__init__(parent)
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
        boton_guardar.setIcon(QIcon(":/assets/svg/cross.svg"))
        boton_guardar.setIconSize(QSize(20, 20))
        boton_guardar.clicked.connect(self.confirmar_guardado)

        boton_salir = QPushButton("Salir")
        boton_salir.setIcon(QIcon(":/assets/svg/exit.svg"))
        boton_salir.setIconSize(QSize(20, 20))
        boton_salir.clicked.connect(self.reject)

        boton_imprimir = QPushButton("Imprimir Historial Clínico")
        boton_imprimir.setIcon(QIcon(":/assets/svg/print.svg"))
        boton_imprimir.setIconSize(QSize(20, 20))
        boton_imprimir.clicked.connect(self.abrir_vista_previa)

        boton_informes = QPushButton("Ver Informes")
        boton_informes.setIcon(QIcon(":/assets/svg/folder.svg"))
        boton_informes.setIconSize(QSize(20, 20))
        boton_informes.clicked.connect(self.abrir_informes)

        botones_layout.addWidget(boton_guardar)
        botones_layout.addWidget(boton_imprimir)
        botones_layout.addWidget(boton_informes)
        botones_layout.addWidget(boton_salir)

        layout.addLayout(botones_layout)

        self.setLayout(layout)

        # self.setWindowState(Qt.WindowMaximized)

    def _init_tab_consulta(self):
        layout = QVBoxLayout()

        datos = self.datos_paciente
        layout.addWidget(QLabel(f"Paciente: {datos['NOMBRE']}"))
        layout.addWidget(QLabel(f"Fecha: {datos.get('FECHA', '')}"))
        layout.addWidget(QLabel(f"Historia Clínica: {datos.get('HCLIN', '')}"))
        layout.addWidget(QLabel(f"Hora: {datos.get('HORA', '')}"))
        layout.addWidget(QLabel(f"Protocolo: {datos.get('PROTOCOLO', '')}"))
        layout.addWidget(QLabel(f"Edad: {datos.get('EDAD', '')}"))
        layout.addWidget(QLabel(f"Sexo: {datos.get('SEXO', '')}"))
        layout.addWidget(QLabel(
            f"Entidad: {datos.get('ENTIDAD', '')}   |   "
            f"Plan: {datos.get('PLAN', '')}   |   "
            f"N° Afiliado: {datos.get('AFILIADO', '')}"
        ))
        layout.addWidget(QLabel(f"Profesional: {datos.get('PROFESIONAL', '')}"))

        # Historial
        layout.addWidget(QLabel("Historial del Paciente:"))

        historial_widget = QWidget()
        historial_layout = QVBoxLayout(historial_widget)
        
        for entrada in self.historial:
            fecha = entrada.get("FECHA", "")
            evolucion = entrada.get("EVOLUCION", "")
            profesional = entrada.get("PROFESIONAL", "")
            hora = entrada.get("HORA", "")
            protocolo = entrada.get("PROTOCOLO", "")

            evolucion_limpia = limpiar_evolucion(evolucion)

            texto = QTextEdit()
            texto.setReadOnly(True)
            texto.setPlainText(
                f"Profesional: {profesional}\n"
                f"Hora: {hora}\n"
                f"Protocolo: {protocolo}\n"
                f"{evolucion_limpia}"
            )
            texto.setFixedHeight(120)

            historial_layout.addWidget(QLabel(str(fecha)))
            historial_layout.addWidget(texto)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(historial_widget)
        scroll.setFixedHeight(300)  

        layout.addWidget(scroll)

        self.tab_consulta.setLayout(layout)

    def _init_tab_evolucion(self):
        layout = QVBoxLayout()
        self.cmb_motivo = ComboBoxBuscador()
        self.txt_evolucion = QTextEdit()
        self.txt_evolucion.setFixedHeight(100)
        self.cmb_diagnostico = ComboBoxBuscador() 
        self.cmb_tratamiento = ComboBoxBuscador()
        self.cmb_examenes = ComboBoxBuscador()
        self.cmb_derivacion = ComboBoxBuscador()

        # Cargar listas desde DB
        self.diagnosticos = obtener_lista_diagnosticos()
        self.examenes = obtener_lista_examenes_complementarios()
        self.motivos = obtener_lista_motivos_consulta()
        self.tratamientos = obtener_lista_tratamientos()
        self.derivacion = obtener_lista_derivaciones()

        # Convertir en listas con formato "desc (codigo)"
        diagnosticos_items = [""] + [f"{desc} ({cod})" for cod, desc in self.diagnosticos]
        examenes_items = [""] + [f"{desc} ({cod})" for cod, desc in self.examenes]
        motivos_items = [""] + [f"{desc} ({cod})" for cod, desc in self.motivos]
        tratamientos_items = [""] + [f"{desc} ({cod})" for cod, desc in self.tratamientos]
        derivacion_items = [""] + [f"{desc} ({cod})" for cod, desc in self.derivacion]

        # Cargar en ComboBox
        self.cmb_diagnostico.setItems(diagnosticos_items)
        self.cmb_examenes.setItems(examenes_items)
        self.cmb_motivo.setItems(motivos_items)
        self.cmb_tratamiento.setItems(tratamientos_items)
        self.cmb_derivacion.setItems(derivacion_items)

        layout.addWidget(QLabel("Motivo de Consulta:"))
        layout.addWidget(self.cmb_motivo)

        layout.addWidget(QLabel("Evolución:"))
        layout.addWidget(self.txt_evolucion)

        layout.addWidget(QLabel("Diagnóstico:"))
        layout.addWidget(self.cmb_diagnostico)

        layout.addWidget(QLabel("Exámenes Complementarios:"))
        layout.addWidget(self.cmb_examenes)

        layout.addWidget(QLabel("Tratamiento:"))
        layout.addWidget(self.cmb_tratamiento)

        layout.addWidget(QLabel("Derivación:"))
        layout.addWidget(self.cmb_derivacion)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container.setLayout(layout)
        scroll.setWidget(container)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        self.tab_evolucion.setLayout(main_layout)

    def confirmar_guardado(self):
        reply = QMessageBox.question(
            self, "Confirmación", "¿Desea guardar esta evolución?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.guardar_evolucion()

    def guardar_evolucion(self):
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
        QMessageBox.information(self, "Éxito", "Evolución guardada correctamente")
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