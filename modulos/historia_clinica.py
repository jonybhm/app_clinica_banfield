# -*- coding: utf-8 -*-
"""
Created on Thu May 15 22:18:21 2025

@author: Jonathan
"""
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QDateEdit, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QStackedLayout
)
from PyQt5.QtCore import QDate, Qt, QTimer
from PyQt5.QtGui import QPixmap, QTextCharFormat, QBrush, QColor
from acceso_db.repositorio_historia import buscar_turnos, obtener_dias_con_turnos
import os


class PantallaHistoriaClinica(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Título
        self.layout.addWidget(QLabel("Historia Clínica"))

        # Layout de filtros
        filtro_layout = QHBoxLayout()
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setDate(QDate.currentDate())
        self.fecha_edit.setCalendarPopup(True)

        # 🎨 Configurar calendario para resaltar días
        self.calendar = self.fecha_edit.calendarWidget()
        self.formato_turno = QTextCharFormat()
        self.formato_turno.setBackground(QBrush(QColor("lightgreen")))
        self.formato_normal = QTextCharFormat()

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

        # --- 🔧 Sección central: tabla + imagen en un QStackedLayout ---
        self.stack_layout = QStackedLayout()
        self.layout.addLayout(self.stack_layout)

        # Tabla de resultados
        self.tabla = QTableWidget()
        self.stack_layout.addWidget(self.tabla)

        # Imagen "no hay turnos"
        self.label_no_turnos = QLabel()
        self.label_no_turnos.setAlignment(Qt.AlignCenter)
        img_path = os.path.join(os.path.dirname(__file__), "../assets/imagenes/no_turnos.png")
        if os.path.exists(img_path):
            self.label_no_turnos.setPixmap(QPixmap(img_path).scaledToWidth(300, Qt.SmoothTransformation))
        else:
            self.label_no_turnos.setText("No hay turnos en esta fecha.")
        self.stack_layout.addWidget(self.label_no_turnos)

        # Botón Nueva Consulta
        btn_nueva = QPushButton("Nueva Consulta")
        btn_nueva.clicked.connect(self.abrir_dialogo_consulta)
        self.layout.addWidget(btn_nueva)

        # Diccionario de timers
        self.timers = {}

        

    def buscar_turnos_ui(self):
        # 🔧 Detener timers anteriores
        for t in self.timers.values():
            t.stop()
        self.timers = {}

        fecha = self.fecha_edit.date().toString("yyyy-MM-dd")
        estado = self.estado_combo.currentText()

        turnos = buscar_turnos(fecha, estado, self.id_profesional, self.nombre_profesional)

        # Mostrar imagen si no hay turnos
        if not turnos:
            self.stack_layout.setCurrentWidget(self.label_no_turnos)
            return
        else:
            self.stack_layout.setCurrentWidget(self.tabla)

        self.tabla.clear()
        self.tabla.setRowCount(len(turnos))
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "Paciente", "Edad", "Sexo", "Recepción", "Espera", "H. Turno", "Profesional"
        ])

        for fila_idx, fila in enumerate(turnos):
            recepcion_val = fila.get("RECEPCION", 0)

            valores_visibles = [
                fila.get("NOMBRE", ""),
                fila.get("EDAD", ""),
                fila.get("SEXO", ""),
                str("OK") if recepcion_val and str(recepcion_val).isdigit() else "NO",  # H. Recepción
                "",  # Espera se rellena después si corresponde
                fila.get("HORA", ""),
                fila.get("PROFESIONAL", ""),
            ]

            for col_idx, valor in enumerate(valores_visibles):
                item = QTableWidgetItem(str(valor))
                if col_idx == 0:
                    item.setData(Qt.UserRole, fila["CODPAC"])
                self.tabla.setItem(fila_idx, col_idx, item)

            # 🚦 Si RECEPCION > 0, arranca temporizador
            if recepcion_val and str(recepcion_val).isdigit():
                self.iniciar_temporizador(fila_idx)


        # 🔧 Resaltar días en el calendario
        self.resaltar_dias_con_turnos()

    def iniciar_temporizador(self, fila_idx):
        # Inicia en 00:00
        self.tabla.setItem(fila_idx, 4, QTableWidgetItem("00:00"))  # columna ESPERA
        self.timers[fila_idx] = QTimer(self)
        self.timers[fila_idx].timeout.connect(lambda f=fila_idx: self.actualizar_espera(f))
        self.timers[fila_idx].start(1000)


    def actualizar_espera(self, fila):
        if not self or not self.tabla:
            return
        if fila >= self.tabla.rowCount():
            return

        item = self.tabla.item(fila, 4)  # columna ESPERA
        if not item:
            return

        valor = item.text()
        try:
            minutos, segundos = map(int, valor.split(":"))
        except:
            minutos, segundos = 0, 0
        segundos += 1
        if segundos >= 60:
            minutos += 1
            segundos = 0
        item.setText(f"{minutos:02}:{segundos:02}")

    def resaltar_dias_con_turnos(self):
        """Marca en verde los días donde el profesional tiene turnos"""
        # limpiar formato
        self.calendar.setDateTextFormat(QDate(), self.formato_normal)

        dias = obtener_dias_con_turnos(self.id_profesional)
        for d in dias:
            qd = QDate(d.year, d.month, d.day)
            self.calendar.setDateTextFormat(qd, self.formato_turno)

    def abrir_dialogo_consulta(self):
        from modulos.dialogo_consulta import DialogoConsulta
        from acceso_db.repositorio_historia import obtener_datos_paciente_y_historial
        from PyQt5.QtWidgets import QDialog

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
        if dlg.exec_() == QDialog.Accepted:
            QMessageBox.information(self, "Guardado", "Evolución registrada con éxito.")

    def closeEvent(self, event):
        # 🔧 Apagar timers al cerrar
        for t in self.timers.values():
            t.stop()
        self.timers = {}
        super().closeEvent(event)

