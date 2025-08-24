# -*- coding: utf-8 -*-
"""
Created on Wed May 21 21:19:31 2025

@author: Jonathan
"""

# modulos/pacientes.py
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from acceso_db.repositorio_historia import obtener_datos_paciente_y_historial, buscar_pacientes, obtener_pacientes
from auxiliar.rtf_utiles import limpiar_evolucion
from modulos.dialogo_consulta import DialogoConsulta
from auxiliar.widgets_personalizados import ComboBoxBuscador


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

        # Nombre con ComboBoxBuscador
        self.combo_nombre = ComboBoxBuscador()
        self.combo_nombre.setPlaceholderText("Buscar por Nombre")
        todos = obtener_pacientes()
        nombres_lista = [p["NOMBRE"] for p in todos]
        self.combo_nombre.setItems(nombres_lista)
        buscador_layout.addWidget(self.combo_nombre)

        # DNI con QLineEdit
        self.input_dni = QLineEdit()
        self.input_dni.setPlaceholderText("Buscar por DNI")
        buscador_layout.addWidget(self.input_dni)

        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.clicked.connect(self.buscar_paciente_ui)
        buscador_layout.addWidget(self.btn_buscar)

        self.layout.addLayout(buscador_layout)

        # Tabla de resultados
        self.tabla = QTableWidget()
        self.layout.addWidget(self.tabla)

        # Botón para abrir historial
        self.btn_historial = QPushButton("Ver Historial / Imprimir")
        self.btn_historial.clicked.connect(self.abrir_dialogo_consulta)
        self.layout.addWidget(self.btn_historial)


    def buscar_paciente_ui(self):
        """ Ejecuta búsqueda por nombre o DNI """
        nombre = self.combo_nombre.currentText().strip()
        dni = self.input_dni.text().strip()

        if not nombre and not dni:
            QMessageBox.warning(self, "Atención", "Ingrese Nombre o DNI para buscar.")
            return

        resultados = buscar_pacientes(nombre, dni)

        if not resultados:
            QMessageBox.information(self, "Sin resultados", "No se encontraron pacientes con esos datos.")
            return

        # Poblar el combo con todos los nombres (para autocompletar en siguientes búsquedas)
        nombres_lista = [r["NOMBRE"] for r in resultados if r.get("NOMBRE")]
        self.combo_nombre.setItems(nombres_lista)

        # Poblar tabla
        self.tabla.clear()
        self.tabla.setRowCount(len(resultados))
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "Nombre", "DNI", "Última Evolución"
        ])

        for fila_idx, fila in enumerate(resultados):
            evolucion = fila.get("EVOLUCION", "")
            evolucion_limpia = limpiar_evolucion(evolucion)

            valores = [
                fila.get("NOMBRE", ""),
                fila.get("DNI", ""),   # ← acá estaba "DOCUMENTO"
                evolucion_limpia[:80] + "..." if evolucion_limpia else ""
            ]
            for col_idx, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                if col_idx == 0:
                    item.setData(Qt.UserRole, fila["CODPAC"])  # guardamos CODPAC oculto
                self.tabla.setItem(fila_idx, col_idx, item)


    def abrir_dialogo_consulta(self):
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
