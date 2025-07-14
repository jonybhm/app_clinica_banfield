# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 13:42:13 2025

@author: Jonathan
"""



from PyQt5.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QTextEdit, QMessageBox, QFormLayout, QTextEdit
)
from PyQt5.QtCore import QDateTime
from datetime import datetime
from auxiliar.rtf_utiles import limpiar_evolucion

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
        layout = QFormLayout()

        datos = self.datos_paciente
        layout.addRow("Paciente:", QLabel(f"{datos['NOMBRE']}"))
        layout.addRow("Fecha:", QLabel(datos.get("FECHA", "")))
        layout.addRow("Historia Clínica:", QLabel(str(datos.get("HCLIN", ""))))
        layout.addRow("Hora:", QLabel(datos.get("HORA", "")))
        layout.addRow("Protocolo:", QLabel(str(datos.get("PROTOCOLO", ""))))
        layout.addRow("Edad:", QLabel(str(datos.get("EDAD", ""))))
        layout.addRow("Sexo:", QLabel(datos.get("SEXO", "")))
        layout.addRow("Entidad:", QLabel(str(datos.get("ENTIDAD", ""))))
        layout.addRow("Profesional:", QLabel(str(datos.get("PROFESIONAL", ""))))

        # Historial
        layout.addRow(QLabel("Historial del Paciente:"))

        for fecha, evolucion in self.historial:
            evolucion_limpia = limpiar_evolucion(evolucion)
            texto = QTextEdit()
            texto.setReadOnly(True)
            texto.setPlainText(evolucion_limpia)
            layout.addRow(QLabel(f"{fecha}"), texto)
            
            #print(evolucion_limpia)
            #layout.addRow(lbl_fecha, lbl_evol)
            
        '''
        # Historial
        layout.addRow(QLabel("Historial del Paciente:"))
        for entrada in self.historial:
            fecha, evolucion = entrada
            layout.addRow(QLabel(f"{fecha}"), QLabel(evolucion[:50] + "..."))
        '''

        self.tab_consulta.setLayout(layout)

    def _init_tab_evolucion(self):
        layout = QVBoxLayout()
        self.txt_motivo = QTextEdit()
        self.txt_diagnostico = QTextEdit()
        self.txt_tratamiento = QTextEdit()
        self.txt_examenes = QTextEdit()
        self.txt_derivacion = QTextEdit()
        self.txt_extra = QTextEdit()

        layout.addWidget(QLabel("Motivo de Consulta:"))
        layout.addWidget(self.txt_motivo)

        layout.addWidget(QLabel("Diagnóstico:"))
        layout.addWidget(self.txt_diagnostico)

        layout.addWidget(QLabel("Tratamiento:"))
        layout.addWidget(self.txt_tratamiento)

        layout.addWidget(QLabel("Exámenes Complementarios:"))
        layout.addWidget(self.txt_examenes)

        layout.addWidget(QLabel("Derivación:"))
        layout.addWidget(self.txt_derivacion)

        layout.addWidget(QLabel("Comentario libre:"))
        layout.addWidget(self.txt_extra)

        self.tab_evolucion.setLayout(layout)

    def confirmar_guardado(self):
        reply = QMessageBox.question(
            self, "Confirmación", "¿Desea guardar esta evolución?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.guardar_evolucion()

    def guardar_evolucion(self):
        texto_final = (
            f"Motivo: {self.txt_motivo.toPlainText()}\n"
            f"Diagnóstico: {self.txt_diagnostico.toPlainText()}\n"
            f"Tratamiento: {self.txt_tratamiento.toPlainText()}\n"
            f"Exámenes: {self.txt_examenes.toPlainText()}\n"
            f"Derivación: {self.txt_derivacion.toPlainText()}\n"
            f"{self.txt_extra.toPlainText()}"
        )

        # Acá podrías insertar en la base de datos usando acceso_db.repositorio_historia.agregar_evolucion()
        print("Guardar en BD: ", texto_final)
        QMessageBox.information(self, "Éxito", "Evolución guardada correctamente")
        self.accept()

