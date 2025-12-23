# -*- coding: utf-8 -*-
"""
Created on Wed May 21 21:19:31 2025

@author: Jonathan
"""

# modulos/pacientes.py
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,QHeaderView,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from acceso_db.repositorio_historia import obtener_datos_paciente_y_historial, buscar_pacientes, obtener_pacientes,buscar_pacientes_triple_factor
from auxiliar.editor_texto.rtf_utiles import limpiar_evolucion
from modulos.dialogo_consulta import DialogoConsulta
from auxiliar.widgets.widgets_personalizados import ComboBoxBuscador
from auxiliar.widgets.spinner import SpinnerDialog
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence
from auxiliar.widgets.widgets_personalizados import formatear_fecha

class PantallaPacientes(QWidget):
    def __init__(self, id_profesional, nombre_profesional):
        super().__init__()
        self.id_profesional = id_profesional
        self.nombre_profesional = nombre_profesional

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Título
        self.layout.addWidget(QLabel("Búsqueda de Pacientes"))

        # Layout buscadores
        buscador_layout = QHBoxLayout()

        # DNI
        self.input_dni = QLineEdit()
        self.input_dni.setPlaceholderText("DNI")
        buscador_layout.addWidget(self.input_dni)

        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre")
        buscador_layout.addWidget(self.input_nombre)

        self.input_apellido = QLineEdit()
        self.input_apellido.setPlaceholderText("Apellido")
        buscador_layout.addWidget(self.input_apellido)

        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.clicked.connect(self.buscar_paciente_ui)
        buscador_layout.addWidget(self.btn_buscar)

        self.layout.addLayout(buscador_layout)

        # Resultados
        self.tabla = QTableWidget()
        self.tabla.setMinimumWidth(1100)
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStretchLastSection(True)


        self.tabla_container = QWidget()
        tabla_layout = QHBoxLayout()
        tabla_layout.addStretch()
        tabla_layout.addWidget(self.tabla)
        tabla_layout.addStretch()
        self.tabla_container.setLayout(tabla_layout)
        self.layout.addWidget(self.tabla_container)

        # Abrir historial
        self.btn_historial = QPushButton("Ver Detalle del Paciente y Evolucionar")
        self.btn_historial.clicked.connect(self.abrir_dialogo_consulta)
        self.layout.addWidget(self.btn_historial)

        # Enter y doble click
        shortcut_enter = QShortcut(QKeySequence(Qt.Key_Return), self.input_dni)
        shortcut_enter.activated.connect(self.buscar_paciente_ui)
        self.tabla.doubleClicked.connect(self.abrir_dialogo_consulta)
        


    def buscar_paciente_ui(self):
        # Mostrar spinner
        spinner = SpinnerDialog("Cargando...")
        spinner.show()
        QApplication.processEvents()

        """ Ejecuta búsqueda por DNI """
        dni = self.input_dni.text().strip()
        nombre = self.input_nombre.text().strip()
        apellido = self.input_apellido.text().strip()

        if not dni and not nombre and not apellido:
            QMessageBox.warning(self, "Atención", "Ingrese al menos un criterio (DNI, Nombre o Apellido).")
            return

        resultados = buscar_pacientes_triple_factor(dni=dni, nombre=nombre, apellido=apellido)

        if not resultados:
            QMessageBox.information(self, "Sin resultados", "No se encontraron pacientes con esos datos.")
            return

        
        # Llenar tabla
        self.tabla.clear()
        self.tabla.setRowCount(len(resultados))
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels([
            "NOMBRE", "DOCUMENTO", "FECHA NACIMIENTO", "ÚLTIMA EVOLUCIÓN"
        ])

        for fila_idx, fila in enumerate(resultados):
            evolucion = fila.get("EVOLUCION", "")
            evolucion_limpia = limpiar_evolucion(evolucion)

            valores = [
                fila.get("NOMBRE", ""),
                fila.get("DOCUMENTO", ""),
                formatear_fecha(fila.get("FENAC", "")),
                evolucion_limpia[:80] + "..." if evolucion_limpia else ""
            ]
            for col_idx, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                if col_idx == 0:
                    item.setData(Qt.UserRole, fila["CODPAC"]) 
                self.tabla.setItem(fila_idx, col_idx, item)

        # Ajustar ancho columnas
        self.tabla.resizeColumnsToContents()
        self.tabla.horizontalHeader().setStretchLastSection(False)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Ordenamiento por columna
        self.tabla.setSortingEnabled(True)

        # Ordenar H. Turno (columna 5)
        self.tabla.sortItems(5, Qt.AscendingOrder)

        self.tabla.setAlternatingRowColors(True)


    def abrir_dialogo_consulta(self):
        # Mostrar spinner
        spinner = SpinnerDialog("Cargando...")
        spinner.show()
        QApplication.processEvents()
        
        """ Abre el historial completo del paciente """
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Atención", "Seleccioná un paciente de la tabla.")
            return

        item_paciente = self.tabla.item(fila, 0)
        codpac = item_paciente.data(Qt.UserRole)

        if not codpac:
            QMessageBox.warning(self, "Error", "No se encontró el código del paciente.")
            return

        datos_paciente, historial = obtener_datos_paciente_y_historial(codpac, self.id_profesional)
        if not datos_paciente:
            QMessageBox.warning(self, "Error", "No se pudieron obtener los datos del paciente.")
            return

        datos_paciente["ID_PROFESIONAL"] = self.id_profesional
        datos_paciente["PROFESIONAL"] = self.nombre_profesional

        dlg = DialogoConsulta(datos_paciente, historial, self)
        dlg.exec_()
