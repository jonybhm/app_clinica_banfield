# -*- coding: utf-8 -*-
"""
Created on Thu May 15 22:18:21 2025

@author: Jonathan
"""

import sys
from PyQt5.QtWidgets import QApplication, QDialog
from main_window import MainWindow
from modulos.login import PantallaLogin


if __name__ == "__main__":
    app = QApplication(sys.argv)

    login = PantallaLogin()
    if login.exec_() == QDialog.Accepted:
        datos_usuario = login.usuario_datos
        main = MainWindow(datos_usuario)  # diccionario al constructor
        main.show()
        sys.exit(app.exec_())
