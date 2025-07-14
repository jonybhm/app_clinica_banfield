# -*- coding: utf-8 -*-
"""
Created on Thu May 15 22:18:21 2025

@author: Jonathan
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QDateEdit, QComboBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import QDate, Qt
from acceso_db.repositorio_historia import buscar_turnos  # módulo de consulta


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
        
        # Boton Nueva Consulta
        btn_nueva = QPushButton("Nueva Consulta")
        btn_nueva.clicked.connect(self.abrir_dialogo_consulta)
        self.layout.addWidget(btn_nueva)

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
        self.tabla.setColumnCount(7)  # solo se mostrarán 7 columnas visibles
        self.tabla.setHorizontalHeaderLabels([
            "Paciente", "Edad", "Sexo", "H. Recepción", "Espera", "H. Turno", "Profesional"
        ])
        
        for fila_idx, fila in enumerate(turnos):
            codpac = fila[0]  # ← lo sacamos aparte
            datos_visibles = fila[1:]  # los 7 datos que van a la tabla
            for col_idx, valor in enumerate(datos_visibles):
                item = QTableWidgetItem(str(valor))
                if col_idx == 0:
                    item.setData(Qt.UserRole, codpac)  # guardamos codpac en la 1ra celda
                self.tabla.setItem(fila_idx, col_idx, item)
        
        print("Turnos encontrados:", turnos)
                
    def abrir_dialogo_consulta(self):
        from modulos.dialogo_consulta import DialogoConsulta
        from acceso_db.repositorio_historia import obtener_datos_paciente_y_historial
        from PyQt5.QtWidgets import QMessageBox, QDialog
    
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Atención", "Seleccioná un paciente de la tabla.")
            return
    
        item_paciente = self.tabla.item(fila, 0)  # ← primera columna tiene UserRole con CODPAC
        codpac = item_paciente.data(Qt.UserRole)
    
        if not codpac:
            QMessageBox.warning(self, "Error", "No se encontró el código del paciente.")
            return
    
        # Usamos el CODPAC y self.id_profesional
        datos_paciente, historial = obtener_datos_paciente_y_historial(codpac, self.id_profesional)
    
        if not datos_paciente:
            QMessageBox.warning(self, "Error", "No se pudieron obtener los datos del paciente.")
            return
    
        dlg = DialogoConsulta(datos_paciente, historial, self)
        if dlg.exec_() == QDialog.Accepted:
            texto_evolucion = (
                f"Motivo: {dlg.txt_motivo.toPlainText()}\n"
                f"Diagnóstico: {dlg.txt_diagnostico.toPlainText()}\n"
                f"Tratamiento: {dlg.txt_tratamiento.toPlainText()}\n"
                f"Exámenes: {dlg.txt_examenes.toPlainText()}\n"
                f"Derivación: {dlg.txt_derivacion.toPlainText()}\n"
                f"{dlg.txt_extra.toPlainText()}"
            )
    
            agregar_evolucion(
                codpac=datos_paciente["CODPAC"],
                hclin=datos_paciente["HCLIN"],
                profes=self.id_profesional,
                evolucion_texto=texto_evolucion,
            )
    
            QMessageBox.information(self, "Guardado", "Evolución registrada con éxito.")