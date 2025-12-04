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
import os

class DialogoInformes(QDialog):
    def __init__(self, codpac, nombre_profesional, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Informes del Paciente")
        self.resize(600, 400)

        self.codpac = codpac
        self.nombre_profesional = nombre_profesional

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Informes disponibles:"))

        self.lista = QListWidget()
        layout.addWidget(self.lista)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_ver = QPushButton("Imprimir Informe Seleccionado")
        self.btn_ver.clicked.connect(self.imprimir_informe)
        btn_layout.addWidget(self.btn_ver)

        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_cerrar)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.cargar_informes()

        # self.setWindowState(Qt.WindowMaximized)

    def cargar_informes(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT PROTOCOLO, FESTUDIO, TIPEA, CMEMO
            FROM dbo.AINFOR
            WHERE CODPAC = ?
            ORDER BY FESTUDIO DESC
        """, (self.codpac,))
        self.informes = []
        for protocolo, festudio, tipe, cmemo in cursor.fetchall():
            info = {
                "PROTOCOLO": protocolo,
                "FESTUDIO": festudio,
                "TIPEA": tipe,
                "CMEMO": cmemo,
                "CODPAC": self.codpac
            }
            self.informes.append(info)
            self.lista.addItem(f"{festudio.strftime('%d/%m/%Y')} - Protocolo {protocolo} ({tipe})")
        conn.close()

    def imprimir_informe(self):
        idx = self.lista.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Atención", "Seleccione un informe primero")
            return

        informe = self.informes[idx]
        archivo = generar_pdf_informe(informe, self.nombre_profesional)
        os.startfile(archivo)
