# -*- coding: utf-8 -*-
"""
Created on Thu May 15 22:18:21 2025

@author: Jonathan
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QDateEdit, QComboBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import QDate
from acceso_db.repositorio_historia import buscar_turnos  # nuestro módulo de consulta

class PantallaHistoriaClinica(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Título
        self.layout.addWidget(QLabel("Historia Clínica"))

        # Filtro por fecha
        filtro_layout = QHBoxLayout()
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setDate(QDate.currentDate())
        self.fecha_edit.setCalendarPopup(True)
        filtro_layout.addWidget(QLabel("Fecha:"))
        filtro_layout.addWidget(self.fecha_edit)

        # Filtro por estado
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(["TODOS", "PENDIENTE", "ATENDIDO"])
        filtro_layout.addWidget(QLabel("Estado:"))
        filtro_layout.addWidget(self.estado_combo)

        # Botón de búsqueda
        self.boton_buscar = QPushButton("Buscar")
        self.boton_buscar.clicked.connect(self.buscar_turnos_ui)
        filtro_layout.addWidget(self.boton_buscar)
        
        

        self.layout.addLayout(filtro_layout)

        # Tabla de resultados
        self.tabla = QTableWidget()
        self.layout.addWidget(self.tabla)

    '''
    def buscar_historias(self):
        fecha = self.fecha_edit.date().toString("yyyy-MM-dd")
        estado = self.estado_combo.currentText()

        historias = obtener_historias(fecha, estado)

        self.tabla.clear()
        self.tabla.setRowCount(len(historias))
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["HCLIN", "CODPAC", "FECHA", "HORA", "ESTADO", "PACIENTE"])

        for fila_idx, fila in enumerate(historias):
            for col_idx, valor in enumerate(fila[:6]):
                item = QTableWidgetItem(str(valor))
                self.tabla.setItem(fila_idx, col_idx, item)
    '''            
    def buscar_turnos_ui(self):
        fecha = self.fecha_edit.date().toString("yyyy-MM-dd")
        estado = self.estado_combo.currentText()
        id_profesional = self.id_profesional  # ← tenés que asignar este valor después del login
    
        turnos = buscar_turnos(fecha, estado, self.id_profesional, self.nombre_profesional)
    
        self.tabla.clear()
        self.tabla.setRowCount(len(turnos))
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "Paciente", "Edad", "Sexo", "H. Recepción", "Espera", "H. Turno", "Profesional"
        ])
    
        for fila_idx, fila in enumerate(turnos):
            for col_idx, valor in enumerate(fila):
                item = QTableWidgetItem(str(valor))
                self.tabla.setItem(fila_idx, col_idx, item)
