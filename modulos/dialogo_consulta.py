# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 13:42:13 2025

@author: Jonathan
"""



from PyQt5.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QTextEdit, QMessageBox, QFormLayout, QTextEdit, QScrollArea, QComboBox, QWidget
)
from PyQt5.QtCore import QDateTime
from datetime import datetime
from auxiliar.rtf_utiles import limpiar_evolucion
from acceso_db.repositorio_historia import obtener_lista_diagnosticos, obtener_lista_motivos_consulta, obtener_lista_examenes_complementarios, obtener_lista_tratamientos, obtener_lista_derivaciones
from auxiliar.widgets_personalizados import ComboBoxBuscador

class DialogoConsulta(QDialog):
    def __init__(self, datos_paciente, historial, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Consulta")
        self.resize(600, 500)

        self.datos_paciente = datos_paciente  # diccionario
        self.historial = historial            # lista de tuplas

        tabs = QTabWidget()
        self.tab_consulta = QWidget()
        self.tab_evolucion = QWidget()

        tabs.addTab(self.tab_consulta, "Consulta")
        tabs.addTab(self.tab_evolucion, "Evolución")

        self._init_tab_consulta()
        self._init_tab_evolucion()

        layout = QVBoxLayout()
        layout.addWidget(tabs)

        # Botón inferior
        boton_guardar = QPushButton("Guardar Evolución")
        boton_guardar.clicked.connect(self.confirmar_guardado)
        layout.addWidget(boton_guardar)

        self.setLayout(layout)

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
        layout.addWidget(QLabel(f"Entidad: {datos.get('ENTIDAD', '')}"))
        layout.addWidget(QLabel(f"Profesional: {datos.get('PROFESIONAL', '')}"))

        # Historial
        layout.addWidget(QLabel("Historial del Paciente:"))

        historial_widget = QWidget()
        historial_layout = QVBoxLayout(historial_widget)
        
        for fecha, evolucion in self.historial:
            evolucion_limpia = limpiar_evolucion(evolucion)
            texto = QTextEdit()
            texto.setReadOnly(True)
            texto.setPlainText(evolucion_limpia)
            texto.setFixedHeight(100)  # altura fija para cada evolución
            historial_layout.addWidget(QLabel(f"{fecha}"))
            historial_layout.addWidget(texto)
            
        '''
        # Historial
        layout.addRow(QLabel("Historial del Paciente:"))
        for entrada in self.historial:
            fecha, evolucion = entrada
            layout.addRow(QLabel(f"{fecha}"), QLabel(evolucion[:50] + "..."))
        '''

        # self.tab_consulta.setLayout(layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(historial_widget)
        scroll.setFixedHeight(300)  # altura máxima del scroll

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

        # Cargar diagnósticos
        self.diagnosticos = obtener_lista_diagnosticos()
        self.examenes = obtener_lista_examenes_complementarios()
        self.motivos = obtener_lista_motivos_consulta()
        self.tratamientos = obtener_lista_tratamientos()
        self.derivacion = obtener_lista_derivaciones()

        # Convertir cada lista (codigo, descripcion) en "descripcion (codigo)"
        diagnosticos_items = [f"{descripcion} ({codigo})" for codigo, descripcion in self.diagnosticos]
        examenes_items = [f"{descripcion} ({codigo})" for codigo, descripcion in self.examenes]
        motivos_items = [f"{descripcion} ({codigo})" for codigo, descripcion in self.motivos]
        tratamientos_items = [f"{descripcion} ({codigo})" for codigo, descripcion in self.tratamientos]
        derivacion_items = [f"{descripcion} ({codigo})" for codigo, descripcion in self.derivacion]

        # Cargar en los ComboBox con setItems
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

        # self.tab_evolucion.setLayout(layout)

        container = QWidget()
        container.setLayout(layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
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
        texto_diag = self.cmb_diagnostico.currentText()
        codigo_diag = None
        if "(" in texto_diag and texto_diag.endswith(")"):
            codigo_diag = texto_diag.split("(")[-1].rstrip(")")

        texto_final = (
            f"Motivo: {self.cmb_motivo.currentText()}\n"
            f"Diagnóstico: {texto_diag} (Código: {codigo_diag})\n"
            f"Tratamiento: {self.cmb_tratamiento.currentText()}\n"
            f"Exámenes: {self.cmb_examenes.currentText()}\n"
            f"Derivación: {self.cmb_derivacion.currentText()}\n"
            f"{self.txt_evolucion.toPlainText()}"
        )

        print("Guardar en BD: ", texto_final)
        QMessageBox.information(self, "Éxito", "Evolución guardada correctamente")
        self.accept()

