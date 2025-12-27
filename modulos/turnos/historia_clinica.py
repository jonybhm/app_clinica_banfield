# -*- coding: utf-8 -*-
"""
Created on Thu May 15 22:18:21 2025

@author: Jonathan
"""
# modulos/historia_clinica.py
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox,
    QDateEdit, QTableWidget, QTableWidgetItem, QMessageBox, QStackedLayout, QHeaderView
)
from PyQt5.QtCore import QDate, Qt, QTimer, QSize
from PyQt5.QtGui import QPixmap, QTextCharFormat, QBrush, QColor, QIcon
import os, datetime
from auxiliar.widgets.spinner import SpinnerDialog
from PyQt5.QtWidgets import QApplication
from auxiliar.rutas import recurso_path
from acceso_db.repositorio_historia import buscar_turnos, obtener_dias_con_turnos, marcar_turno_atendido,paciente_tiene_evolucion
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence

from workers.turnos.buscar_turnos_worker import BuscarTurnosWorker
from workers.turnos.dias_con_turnos_worker import DiasConTurnosWorker
from workers.base.task_manager import TaskManager
from workers.pacientes.datos_paciente_worker import DatosPacienteWorker
from modulos.evolucion.dialogo_consulta import DialogoConsulta

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
        self.boton_buscar.setIcon(QIcon(":/assets/svg/search.svg"))
        self.boton_buscar.setIconSize(QSize(20, 20))
        self.boton_buscar.clicked.connect(self.buscar_turnos_ui)
        filtro_layout.addWidget(self.boton_buscar)

        self.layout.addLayout(filtro_layout)

        self.stack_layout = QStackedLayout()
        self.layout.addLayout(self.stack_layout)

        # --- CONTENEDOR PRINCIPAL (marca de agua + tabla centrada) ---
        self.contenedor_resultados = QWidget()
        self.fondo_layout = QStackedLayout(self.contenedor_resultados)

        

        # ---- TABLA centrada ----
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

        # capa frontal = tabla
        self.fondo_layout.addWidget(self.tabla_container)

        # añadir al stacked principal
        self.stack_layout.addWidget(self.contenedor_resultados)


        # Imagen "no hay turnos"
        self.label_no_turnos = QLabel()
        self.label_no_turnos.setAlignment(Qt.AlignCenter)
        img_path = os.path.join(os.path.dirname(__file__), "../assets/imagenes/no_turnos.png")
        img_path = recurso_path(img_path)
        
        if os.path.exists(img_path):
            self.label_no_turnos.setPixmap(QPixmap(img_path).scaledToWidth(300, Qt.SmoothTransformation))
        else:
            self.label_no_turnos.setText("No hay turnos en esta fecha.")
        self.stack_layout.addWidget(self.label_no_turnos)

        # Ver Detalle del Paciente
        btn_nueva = QPushButton("Ver Detalle del Paciente y Evolucionar")
        btn_nueva.setIcon(QIcon(":/assets/svg/cross.svg"))
        btn_nueva.setIconSize(QSize(20, 20))
        btn_nueva.clicked.connect(self.abrir_dialogo_consulta)
        self.layout.addWidget(btn_nueva)

        # Diccionario de timers
        self.timers = {}
        
        # Enter y doble click
        shortcut_enter = QShortcut(QKeySequence(Qt.Key_Return), self)
        shortcut_enter.activated.connect(self.buscar_turnos_ui)

        self.tabla.doubleClicked.connect(self.abrir_dialogo_consulta)

    def buscar_turnos_ui(self):
        fecha = self.fecha_edit.date().toString("yyyy-MM-dd")
        estado = self.estado_combo.currentText()

        task = BuscarTurnosWorker(
            fecha,
            estado,
            self.id_profesional,
            self.nombre_profesional
        )

        task.signals.finished.connect(self._mostrar_turnos)
        task.signals.error.connect(self._error_turnos)

        TaskManager.instance().run(task, "Buscando turnos...")
    
    def _mostrar_turnos(self, turnos):
        if not turnos:
            self.stack_layout.setCurrentWidget(self.label_no_turnos)
            return
        else:
            self.stack_layout.setCurrentWidget(self.contenedor_resultados)

        self.tabla.clear()
        self.tabla.setRowCount(0)
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "Paciente", "Edad", "Sexo", "Recepción",
            "Espera", "H. Turno", "Profesional", "Atendido"
        ])

        fecha = self.fecha_edit.date().toString("yyyy-MM-dd")
        fecha_hoy = QDate.currentDate().toString("yyyy-MM-dd")

        for fila in turnos:
            codpac = fila.get("CODPAC")
            nombre = fila.get("NOMBRE")

            if not codpac or not nombre:
                continue

            recepcion_txt = fila.get("RECEPCION", "❌ FALTA")
            anulado = fila.get("ANULADO", 0)
            hora_bruta = fila.get("HORA")
            hora_turno = hora_bruta if hora_bruta not in (None, "", "-", "0") else "SIN TURNO PROGRAMADO"
            tiene_evo = fila.get("TIENE_EVOLUCION", False)

            row = self.tabla.rowCount()
            self.tabla.insertRow(row)

            valores = [
                nombre,
                fila.get("EDAD", ""),
                fila.get("SEXO", ""),
                recepcion_txt,
                "",
                hora_turno,
                fila.get("PROFESIONAL", "")
            ]

            for col, val in enumerate(valores):
                item = QTableWidgetItem(str(val))
                if col == 0:
                    item.setData(Qt.UserRole, codpac)
                self.tabla.setItem(row, col, item)

            # Estado atención
            estado = "✔️ ATENDIDO" if fila.get("ATENDHC") or tiene_evo else "❌ FALTA ATENDER"
            self.tabla.setItem(row, 7, QTableWidgetItem(estado))

            # Colorear anulados
            if anulado == 1:
                for c in range(self.tabla.columnCount()):
                    self.tabla.item(row, c).setForeground(QBrush(QColor("#888888")))
                    self.tabla.item(row, c).setBackground(QBrush(QColor("#f5f5f5")))

            # Temporizador
            if fecha == fecha_hoy and "✔️" in recepcion_txt and not tiene_evo and anulado == 0:
                if codpac not in self.timers:
                    self.iniciar_temporizador(row, codpac, fila.get("HORAREC"))
                else:
                    self.tabla.setItem(row, 4, QTableWidgetItem(self.timers[codpac]["tiempo"]))

        self.tabla.resizeColumnsToContents()
        self.tabla.horizontalHeader().setStretchLastSection(False)
        self.tabla.setSortingEnabled(True)
        self.tabla.sortItems(5, Qt.AscendingOrder)
        self.tabla.setAlternatingRowColors(True)

        self.resaltar_dias_con_turnos()
    
    def _error_turnos(self, error):
        QMessageBox.critical(self, "Error", error)


    def iniciar_temporizador(self, fila_idx, codpac, horarec_val):
        try:
            if horarec_val:                
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

        # actualizar celda visible
        filas = self.tabla.rowCount()
        for f in range(filas):
            item_pac = self.tabla.item(f, 0)
            if item_pac and item_pac.data(Qt.UserRole) == codpac:
                self.tabla.setItem(f, 4, QTableWidgetItem(nuevo))
                break

    def resaltar_dias_con_turnos(self):
        task = DiasConTurnosWorker(self.id_profesional)
        task.signals.finished.connect(self._pintar_dias)
        TaskManager.instance().run(task, "Cargando calendario...")

    def _pintar_dias(self, dias):
        self.calendar.setDateTextFormat(QDate(), self.formato_normal)
        for d in dias:
            qd = QDate(d.year, d.month, d.day)
            self.calendar.setDateTextFormat(qd, self.formato_turno)

    def abrir_dialogo_consulta(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Atención", "Seleccioná un paciente.")
            return

        codpac = self.tabla.item(fila, 0).data(Qt.UserRole)

        task = DatosPacienteWorker(codpac, self.id_profesional)
        task.signals.finished.connect(self._abrir_dialogo_con_datos)
        task.signals.error.connect(lambda e: QMessageBox.critical(self, "Error", e))

        TaskManager.instance().run(task, "Cargando historia clínica...")

    def _abrir_dialogo_con_datos(self, resultado):
        datos_paciente, historial = resultado

        if not datos_paciente or not datos_paciente.get("HCLIN"):
            QMessageBox.critical(self, "Error", "Datos incompletos del paciente.")
            return

        datos_paciente["ID_PROFESIONAL"] = self.id_profesional
        datos_paciente["PROFESIONAL"] = self.nombre_profesional

        dlg = DialogoConsulta(datos_paciente, historial, self)
        dlg.exec_()


    def closeEvent(self, event):
        # Apagar timers al cerrar
        for t in self.timers.values():
            t["timer"].stop()
        self.timers = {}
        super().closeEvent(event)
