# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 13:42:13 2025

@author: Jonathan
"""


# modulos/dialogo_informes.py
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QListWidget, QMessageBox, QHBoxLayout
from auxiliar.pdf_utiles import generar_pdf_informe
from acceso_db.conexion import obtener_conexion
from workers.informes.informes_previos_worker import InformesPreviosWorker
from workers.base.task_manager import TaskManager
from auxiliar.pdf_utiles import generar_pdf_informe
import os

class DialogoInformes(QDialog):
    def __init__(self, informes, nombre_profesional, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Informes del Paciente")
        self.resize(600, 400)

        self.informes = informes
        self.nombre_profesional = nombre_profesional

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Informes disponibles:"))

        self.lista = QListWidget()
        layout.addWidget(self.lista)

        btn_layout = QHBoxLayout()
        self.btn_ver = QPushButton("Imprimir Informe Seleccionado")
        self.btn_ver.clicked.connect(self.imprimir_informe)
        btn_layout.addWidget(self.btn_ver)

        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_cerrar)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # ✅ CORRECTO
        self._mostrar_informes(self.informes)




    def _mostrar_informes(self, resultados):
        self.lista.clear()
        self.informes = resultados

        if not resultados:
            self.lista.addItem("No hay informes disponibles.")
            return

        for info in resultados:
            texto = f"{info['FESTUDIO'].strftime('%d/%m/%Y')} - Protocolo {info['PROTOCOLO']} ({info['TIPEA']})"
            self.lista.addItem(texto)

    def imprimir_informe(self):
        idx = self.lista.currentRow()

        if idx < 0:
            QMessageBox.warning(self, "Atención", "Seleccione un informe primero")
            return

        try:
            informe = self.informes[idx]
            archivo = generar_pdf_informe(informe, self.nombre_profesional)

            if not os.path.exists(archivo):
                raise FileNotFoundError("El PDF no se generó correctamente.")

            os.startfile(archivo)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{e}")


    def log_error(self, mensaje):
        ruta_log = os.path.join(os.path.expanduser("~"), "icb_error_log.txt")
        with open(ruta_log, "a", encoding="utf-8") as f:
            f.write(mensaje + "\n")