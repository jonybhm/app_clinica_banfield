# -*- coding: utf-8 -*-
"""
Created on Wed May 21 21:19:31 2025

@author: Jonathan
"""

# modulos/login.py
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QApplication
from acceso_db.repositorio_usuario import login_usuario, obtener_lista_usuarios
from auxiliar.widgets_personalizados import ComboBoxBuscador
from auxiliar.rutas import recurso_path

class PantallaLogin(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Iniciar Sesión")
        self.setModal(True)
        self.usuario_datos = None

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Usuario"))

        self.usuario_combo = ComboBoxBuscador()
        self.usuario_combo.setItems(obtener_lista_usuarios())
        layout.addWidget(self.usuario_combo)

        layout.addWidget(QLabel("Contraseña"))
        self.clave_input = QLineEdit()
        self.clave_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.clave_input)

        boton = QPushButton("Ingresar")
        boton.clicked.connect(self.validar_login)
        layout.addWidget(boton)

        self.setLayout(layout)
        QApplication.setStyle("Fusion")
        self._aplicar_tema_oscuro()

    def validar_login(self):
        usuario = self.usuario_combo.currentText()
        clave = self.clave_input.text()

        datos = login_usuario(usuario.strip(), clave)
        if datos:
            self.usuario_datos = datos
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos o inactivo")

    def _aplicar_tema_oscuro(self):
        try:
            with open(recurso_path("assets/styles/estilo_oscuro.qss"), "r") as f:
                estilo = f.read()
                self.setStyleSheet(estilo)
        except FileNotFoundError:
            print("Archivo de estilos no encontrado")

