# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 19:26:31 2025

@author: Jonathan
"""

# modulos/admin_usuarios.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QComboBox, QPushButton, QLabel
from modulos.permisos_widget import PermisosWidget
from modulos.datos_usuario_widget import DatosUsuarioWidget
from acceso_db.repositorio_usuario import obtener_usuarios_con_codigo
from auxiliar.widgets.widgets_personalizados import ComboBoxBuscador

class AdminUsuarios(QDialog):  
    def __init__(self, id_usuario, parent=None):
        super().__init__(parent)
        self.id_usuario = id_usuario
        self.setWindowTitle("Administración de Usuarios")
        self.resize(900, 600)

        layout = QVBoxLayout(self)

        self.usuario_combo = ComboBoxBuscador()
        
        # Obtenemos lista y la ordenamos alfabéticamente por nombre
        usuarios = obtener_usuarios_con_codigo()
        usuarios.sort(key=lambda x: x[1].lower())

        # Guardamos mapping código -> nombre
        self._mapa_usuarios = {nombre: codigo for codigo, nombre in usuarios}
        self.usuario_combo.setItems([nombre for _, nombre in usuarios])

        self.btn_cargar = QPushButton("Cargar Usuario")
        self.btn_cargar.clicked.connect(self.cargar_usuario)

        layout.addWidget(QLabel("Seleccionar Usuario:"))
        layout.addWidget(self.usuario_combo)
        layout.addWidget(self.btn_cargar)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

    def cargar_usuario(self):
        nombre = self.usuario_combo.currentText()
        codigo_usuario = self._mapa_usuarios.get(nombre)
        if not codigo_usuario:
            return
        self.tabs.clear()
        self.tabs.addTab(PermisosWidget(codigo_usuario), "Permisos")
        self.tabs.addTab(DatosUsuarioWidget(codigo_usuario), "Datos Personales")

