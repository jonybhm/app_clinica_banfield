# -*- coding: utf-8 -*-
"""
Created on Thu May 15 22:18:21 2025

@author: Jonathan
"""
# modulos/historia_clinica.py
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QDateEdit, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QStackedLayout
)
from PyQt5.QtCore import QDate, Qt, QTimer
from PyQt5.QtGui import QPixmap, QTextCharFormat, QBrush, QColor
from acceso_db.repositorio_historia import buscar_turnos, obtener_dias_con_turnos
import os
from acceso_db.repositorio_historia import marcar_turno_atendido    
import datetime
from auxiliar.widgets.spinner import SpinnerDialog
from PyQt5.QtWidgets import QApplication

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

        # Configurar calendario para resaltar días
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

        # --- Mostrar spinner ---
        spinner = SpinnerDialog("Buscando turnos...")
        spinner.show()
        QApplication.processEvents()
        
        fecha = self.fecha_edit.date().toString("yyyy-MM-dd")
        estado = self.estado_combo.currentText()
        turnos = buscar_turnos(fecha, estado, self.id_profesional, self.nombre_profesional)

        if not turnos:
            self.stack_layout.setCurrentWidget(self.label_no_turnos)
            return
        else:
            self.stack_layout.setCurrentWidget(self.tabla)

        self.tabla.clear()
        self.tabla.setRowCount(len(turnos))
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "Paciente", "Edad", "Sexo", "Recepción", "Espera", "H. Turno", "Profesional", "Atendido"
        ])

        fecha_hoy = QDate.currentDate().toString("yyyy-MM-dd")

        for fila_idx, fila in enumerate(turnos):
            codpac = fila["CODPAC"]
            recepcion_val = fila.get("RECEPCION", 0)
            atendido_val = fila.get("ATENDIDO", 0)

            valores_visibles = [
                fila.get("NOMBRE", ""),
                fila.get("EDAD", ""),
                fila.get("SEXO", ""),
                "✔️" if recepcion_val and str(recepcion_val).isdigit() else "❌",
                "",  # Espera (se rellena más abajo)
                fila.get("HORA", ""),
                fila.get("PROFESIONAL", "")
            ]

            # Columnas normales
            for col_idx, valor in enumerate(valores_visibles):
                item = QTableWidgetItem(str(valor))
                if col_idx == 0:
                    item.setData(Qt.UserRole, codpac)
                self.tabla.setItem(fila_idx, col_idx, item)

            # Columna Atendido como combo
            combo = QComboBox()
            combo.addItems(["❌ FALTA ATENDER", "✔️ ATENDIDO"])
            combo.setCurrentIndex(1 if atendido_val == 1 else 0)
            combo.wheelEvent = lambda event: event.ignore()  # 🔒 desactivar scroll accidental
            combo.currentIndexChanged.connect(
                lambda idx, f=fila_idx, cp=codpac: self.cambiar_atendido(idx, f, cp)
            )
            self.tabla.setCellWidget(fila_idx, 7, combo)

            # --- Timer ---
            if fecha == fecha_hoy and recepcion_val and str(recepcion_val).isdigit() and atendido_val == 0:
                if codpac not in self.timers:
                    # Primera vez → iniciar
                    self.iniciar_temporizador(fila_idx, codpac, recepcion_val)
                else:
                    # Ya existía → recuperar valor de texto
                    tiempo_actual = self.timers[codpac]["tiempo"]
                    self.tabla.setItem(fila_idx, 4, QTableWidgetItem(tiempo_actual))

        self.resaltar_dias_con_turnos()

    

    def cambiar_atendido(self, idx, fila_idx, codpac):
        if idx == 1:  # ✔️
            fecha_turno = self.fecha_edit.date().toString("yyyy-MM-dd")
            marcar_turno_atendido(codpac, fecha_turno, self.id_profesional)

            # detener timer
            if codpac in self.timers:
                self.timers[codpac]["timer"].stop()
                del self.timers[codpac]

            self.tabla.setItem(fila_idx, 7, QTableWidgetItem("✔️ ATENDIDO"))



    def iniciar_temporizador(self, fila_idx, codpac, horarec_val):
        import datetime
        try:
            if horarec_val:
                # horarec_val es tipo datetime o string con la hora → normalizar
                if isinstance(horarec_val, datetime.time):
                    inicio = datetime.datetime.combine(datetime.date.today(), horarec_val)
                elif isinstance(horarec_val, str):
                    h, m, *_ = map(int, horarec_val.split(":"))
                    inicio = datetime.datetime.combine(datetime.date.today(), datetime.time(h, m))
                else:
                    inicio = datetime.datetime.now()

                ahora = datetime.datetime.now()
                delta = ahora - inicio
                segundos_totales = int(delta.total_seconds())
                total_min, total_sec = divmod(segundos_totales, 60)
            else:
                total_min, total_sec = 0, 0

        except Exception as e:
            print("Error en iniciar_temporizador:", e)
            total_min, total_sec = 0, 0

        tiempo_str = f"{total_min:02}:{total_sec:02}"
        self.tabla.setItem(fila_idx, 4, QTableWidgetItem(tiempo_str))

        timer = QTimer(self)
        timer.timeout.connect(lambda cp=codpac: self.actualizar_espera(cp))
        timer.start(1000)

        self.timers[codpac] = {"timer": timer, "tiempo": tiempo_str}


    def actualizar_espera(self, codpac):
        if codpac not in self.timers:
            return
        tiempo_str = self.timers[codpac]["tiempo"]

        try:
            minutos, segundos = map(int, tiempo_str.split(":"))
        except:
            minutos, segundos = 0, 0
        segundos += 1
        if segundos >= 60:
            minutos += 1
            segundos = 0
        nuevo = f"{minutos:02}:{segundos:02}"

        # actualizar memoria
        self.timers[codpac]["tiempo"] = nuevo

        # actualizar celda visible (si sigue en pantalla)
        filas = self.tabla.rowCount()
        for f in range(filas):
            item_pac = self.tabla.item(f, 0)
            if item_pac and item_pac.data(Qt.UserRole) == codpac:
                self.tabla.setItem(f, 4, QTableWidgetItem(nuevo))
                break

    def resaltar_dias_con_turnos(self):
        """Marca en verde los días donde el profesional tiene turnos"""
        # limpiar formato
        self.calendar.setDateTextFormat(QDate(), self.formato_normal)

        dias = obtener_dias_con_turnos(self.id_profesional)
        for d in dias:
            qd = QDate(d.year, d.month, d.day)
            self.calendar.setDateTextFormat(qd, self.formato_turno)

    from acceso_db.repositorio_historia import marcar_turno_atendido

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
            # 1. Actualizar en la BD
            fecha_turno = self.fecha_edit.date().toString("yyyy-MM-dd")
            marcar_turno_atendido(codpac, fecha_turno, self.id_profesional)

            # 2. Refrescar columna ATENDIDO en la tabla
            self.tabla.setItem(fila, 7, QTableWidgetItem("✔️"))

            # 3. Detener temporizador de espera para ese paciente
            if fila in self.timers:
                self.timers[fila].stop()
                del self.timers[fila]

            QMessageBox.information(self, "Guardado", "Evolución registrada con éxito.")


    def closeEvent(self, event):
        # 🔧 Apagar timers al cerrar
        for t in self.timers.values():
            t.stop()
        self.timers = {}
        super().closeEvent(event)

