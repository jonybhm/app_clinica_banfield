# -*- coding: utf-8 -*-
"""
Created on Thu May 15 22:18:21 2025

@author: Jonathan
"""
# main.py
import sys, time
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from main_window import MainWindow
from modulos.login import PantallaLogin
from auxiliar.rutas import recurso_path

class ControladorApp:
    def __init__(self, app):
        self.app = app
        self.login_window = None
        self.main_window = None

    def mostrar_login(self):
        self.login_window = PantallaLogin()
        self.login_window.accepted.connect(self._login_aceptado)
        self.login_window.show()

    def _login_aceptado(self):
        datos_usuario = self.login_window.usuario_datos
        self.login_window.close()
        self.mostrar_main(datos_usuario)

    def mostrar_main(self, datos_usuario):
        self.main_window = MainWindow(datos_usuario)
        self.main_window.logout_signal.connect(self._cerrar_sesion)
        self.main_window.show()

    def _cerrar_sesion(self):
        self.main_window.close()
        self.mostrar_login()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Splash screen
    splash = QSplashScreen(QPixmap(recurso_path("assets/spinner/logo-carga.png")))
    splash.showMessage("Cargando...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
    splash.show()
    app.processEvents()

    time.sleep(2)

    controlador = ControladorApp(app)
    controlador.mostrar_login()
    splash.finish(controlador.login_window)

    sys.exit(app.exec_())
